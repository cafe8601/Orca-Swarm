import { initDatabase, insertEvent, getFilterOptions, getRecentEvents } from './db';
import type { HookEvent } from './types';
import { 
  createTheme, 
  updateThemeById, 
  getThemeById, 
  searchThemes, 
  deleteThemeById, 
  exportThemeById, 
  importTheme,
  getThemeStats 
} from './theme';

// Initialize database
initDatabase();

// Store WebSocket clients
const wsClients = new Set<any>();

// Metrics collection
const metrics = {
  events_received_total: 0,
  events_failed_total: 0,
  websocket_connections_active: 0,
  websocket_connections_total: 0,
  websocket_disconnections_total: 0,
  http_requests_total: 0,
  http_requests_by_path: new Map<string, number>(),
  server_start_time: Date.now(),
};

// SECURITY WARNING: This server currently has NO authentication or authorization!
// CORS is set to '*' allowing all origins - suitable ONLY for development.
// For production use:
// 1. Implement authentication (API keys, JWT, OAuth)
// 2. Restrict CORS to specific origins via ALLOWED_ORIGINS env variable
// 3. Add rate limiting to prevent DoS attacks
// 4. Implement input validation and sanitization
// 5. Use HTTPS in production (configure reverse proxy)

const isDevelopment = process.env.NODE_ENV !== 'production';
const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || ['*'];

// API Key Authentication (optional in development, required in production)
const API_KEY = process.env.OBSERVABILITY_API_KEY;
const requireAuth = !isDevelopment || process.env.REQUIRE_AUTH === 'true';

// Authentication helper
function isAuthenticated(req: Request): boolean {
  if (!requireAuth) {
    return true;  // Skip auth in development (unless REQUIRE_AUTH=true)
  }

  if (!API_KEY) {
    console.warn('[SECURITY] OBSERVABILITY_API_KEY not set but auth is required');
    return false;
  }

  const authHeader = req.headers.get('x-api-key') || req.headers.get('authorization');
  return authHeader === API_KEY || authHeader === `Bearer ${API_KEY}`;
}

// Create Bun server with HTTP and WebSocket support
const server = Bun.serve({
  port: 4000,

  async fetch(req: Request) {
    const url = new URL(req.url);

    // Track HTTP requests
    metrics.http_requests_total++;
    const pathCount = metrics.http_requests_by_path.get(url.pathname) || 0;
    metrics.http_requests_by_path.set(url.pathname, pathCount + 1);

    // Handle CORS
    const origin = req.headers.get('origin') || '*';
    const allowOrigin = isDevelopment || allowedOrigins.includes('*') || allowedOrigins.includes(origin)
      ? origin
      : allowedOrigins[0] || '*';

    const headers = {
      'Access-Control-Allow-Origin': allowOrigin,
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Log security warning in production if using permissive CORS
    if (!isDevelopment && allowOrigin === '*') {
      console.warn(
        '[SECURITY WARNING] Using wildcard CORS in production. ' +
        'Set ALLOWED_ORIGINS environment variable to restrict origins.'
      );
    }
    
    // Handle preflight
    if (req.method === 'OPTIONS') {
      return new Response(null, { headers });
    }

    // GET /health - Health check endpoint
    if (url.pathname === '/health' && req.method === 'GET') {
      const uptime = (Date.now() - metrics.server_start_time) / 1000;
      const health = {
        status: 'healthy',
        uptime_seconds: uptime,
        websocket_clients: wsClients.size,
        events_received: metrics.events_received_total,
        timestamp: new Date().toISOString(),
      };
      return new Response(JSON.stringify(health), {
        headers: { ...headers, 'Content-Type': 'application/json' }
      });
    }

    // GET /metrics - Prometheus metrics endpoint
    if (url.pathname === '/metrics' && req.method === 'GET') {
      const uptime = (Date.now() - metrics.server_start_time) / 1000;

      // Generate Prometheus text format
      const prometheusMetrics = [
        '# HELP events_received_total Total number of events received',
        '# TYPE events_received_total counter',
        `events_received_total ${metrics.events_received_total}`,
        '',
        '# HELP events_failed_total Total number of failed event processing',
        '# TYPE events_failed_total counter',
        `events_failed_total ${metrics.events_failed_total}`,
        '',
        '# HELP websocket_connections_active Current active WebSocket connections',
        '# TYPE websocket_connections_active gauge',
        `websocket_connections_active ${wsClients.size}`,
        '',
        '# HELP websocket_connections_total Total WebSocket connections',
        '# TYPE websocket_connections_total counter',
        `websocket_connections_total ${metrics.websocket_connections_total}`,
        '',
        '# HELP websocket_disconnections_total Total WebSocket disconnections',
        '# TYPE websocket_disconnections_total counter',
        `websocket_disconnections_total ${metrics.websocket_disconnections_total}`,
        '',
        '# HELP http_requests_total Total HTTP requests',
        '# TYPE http_requests_total counter',
        `http_requests_total ${metrics.http_requests_total}`,
        '',
        '# HELP server_uptime_seconds Server uptime in seconds',
        '# TYPE server_uptime_seconds gauge',
        `server_uptime_seconds ${uptime}`,
        '',
      ];

      // Add per-path metrics
      if (metrics.http_requests_by_path.size > 0) {
        prometheusMetrics.push('# HELP http_requests_by_path_total HTTP requests by path');
        prometheusMetrics.push('# TYPE http_requests_by_path_total counter');
        metrics.http_requests_by_path.forEach((count, path) => {
          prometheusMetrics.push(`http_requests_by_path_total{path="${path}"} ${count}`);
        });
        prometheusMetrics.push('');
      }

      return new Response(prometheusMetrics.join('\n'), {
        headers: { 'Content-Type': 'text/plain; version=0.0.4' }
      });
    }

    // POST /events - Receive new events
    if (url.pathname === '/events' && req.method === 'POST') {
      // Authentication check
      if (!isAuthenticated(req)) {
        return new Response(JSON.stringify({ error: 'Unauthorized' }), {
          status: 401,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }

      try {
        const event: HookEvent = await req.json();
        
        // Validate required fields
        if (!event.source_app || !event.session_id || !event.hook_event_type || !event.payload) {
          metrics.events_failed_total++;
          return new Response(JSON.stringify({ error: 'Missing required fields' }), {
            status: 400,
            headers: { ...headers, 'Content-Type': 'application/json' }
          });
        }

        // Insert event into database
        const savedEvent = insertEvent(event);
        metrics.events_received_total++;
        
        // Broadcast to all WebSocket clients
        const message = JSON.stringify({ type: 'event', data: savedEvent });
        wsClients.forEach(client => {
          try {
            client.send(message);
          } catch (err) {
            // Client disconnected, remove from set
            wsClients.delete(client);
          }
        });
        
        return new Response(JSON.stringify(savedEvent), {
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      } catch (error) {
        console.error('Error processing event:', error);
        metrics.events_failed_total++;
        return new Response(JSON.stringify({ error: 'Invalid request' }), {
          status: 400,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
    }
    
    // GET /events/filter-options - Get available filter options
    if (url.pathname === '/events/filter-options' && req.method === 'GET') {
      const options = getFilterOptions();
      return new Response(JSON.stringify(options), {
        headers: { ...headers, 'Content-Type': 'application/json' }
      });
    }
    
    // GET /events/recent - Get recent events
    if (url.pathname === '/events/recent' && req.method === 'GET') {
      const limit = parseInt(url.searchParams.get('limit') || '100');
      const events = getRecentEvents(limit);
      return new Response(JSON.stringify(events), {
        headers: { ...headers, 'Content-Type': 'application/json' }
      });
    }
    
    // Theme API endpoints
    
    // POST /api/themes - Create a new theme
    if (url.pathname === '/api/themes' && req.method === 'POST') {
      try {
        const themeData = await req.json();
        const result = await createTheme(themeData);
        
        const status = result.success ? 201 : 400;
        return new Response(JSON.stringify(result), {
          status,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      } catch (error) {
        console.error('Error creating theme:', error);
        return new Response(JSON.stringify({ 
          success: false, 
          error: 'Invalid request body' 
        }), {
          status: 400,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
    }
    
    // GET /api/themes - Search themes
    if (url.pathname === '/api/themes' && req.method === 'GET') {
      const query = {
        query: url.searchParams.get('query') || undefined,
        isPublic: url.searchParams.get('isPublic') ? url.searchParams.get('isPublic') === 'true' : undefined,
        authorId: url.searchParams.get('authorId') || undefined,
        sortBy: url.searchParams.get('sortBy') as any || undefined,
        sortOrder: url.searchParams.get('sortOrder') as any || undefined,
        limit: url.searchParams.get('limit') ? parseInt(url.searchParams.get('limit')!) : undefined,
        offset: url.searchParams.get('offset') ? parseInt(url.searchParams.get('offset')!) : undefined,
      };
      
      const result = await searchThemes(query);
      return new Response(JSON.stringify(result), {
        headers: { ...headers, 'Content-Type': 'application/json' }
      });
    }
    
    // GET /api/themes/:id - Get a specific theme
    if (url.pathname.startsWith('/api/themes/') && req.method === 'GET') {
      const id = url.pathname.split('/')[3];
      if (!id) {
        return new Response(JSON.stringify({ 
          success: false, 
          error: 'Theme ID is required' 
        }), {
          status: 400,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
      
      const result = await getThemeById(id);
      const status = result.success ? 200 : 404;
      return new Response(JSON.stringify(result), {
        status,
        headers: { ...headers, 'Content-Type': 'application/json' }
      });
    }
    
    // PUT /api/themes/:id - Update a theme
    if (url.pathname.startsWith('/api/themes/') && req.method === 'PUT') {
      const id = url.pathname.split('/')[3];
      if (!id) {
        return new Response(JSON.stringify({ 
          success: false, 
          error: 'Theme ID is required' 
        }), {
          status: 400,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
      
      try {
        const updates = await req.json();
        const result = await updateThemeById(id, updates);
        
        const status = result.success ? 200 : 400;
        return new Response(JSON.stringify(result), {
          status,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      } catch (error) {
        console.error('Error updating theme:', error);
        return new Response(JSON.stringify({ 
          success: false, 
          error: 'Invalid request body' 
        }), {
          status: 400,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
    }
    
    // DELETE /api/themes/:id - Delete a theme
    if (url.pathname.startsWith('/api/themes/') && req.method === 'DELETE') {
      const id = url.pathname.split('/')[3];
      if (!id) {
        return new Response(JSON.stringify({ 
          success: false, 
          error: 'Theme ID is required' 
        }), {
          status: 400,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
      
      const authorId = url.searchParams.get('authorId');
      const result = await deleteThemeById(id, authorId || undefined);
      
      const status = result.success ? 200 : (result.error?.includes('not found') ? 404 : 403);
      return new Response(JSON.stringify(result), {
        status,
        headers: { ...headers, 'Content-Type': 'application/json' }
      });
    }
    
    // GET /api/themes/:id/export - Export a theme
    if (url.pathname.match(/^\/api\/themes\/[^\/]+\/export$/) && req.method === 'GET') {
      const id = url.pathname.split('/')[3];
      
      const result = await exportThemeById(id);
      if (!result.success) {
        const status = result.error?.includes('not found') ? 404 : 400;
        return new Response(JSON.stringify(result), {
          status,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
      
      return new Response(JSON.stringify(result.data), {
        headers: { 
          ...headers, 
          'Content-Type': 'application/json',
          'Content-Disposition': `attachment; filename="${result.data.theme.name}.json"`
        }
      });
    }
    
    // POST /api/themes/import - Import a theme
    if (url.pathname === '/api/themes/import' && req.method === 'POST') {
      try {
        const importData = await req.json();
        const authorId = url.searchParams.get('authorId');
        
        const result = await importTheme(importData, authorId || undefined);
        
        const status = result.success ? 201 : 400;
        return new Response(JSON.stringify(result), {
          status,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      } catch (error) {
        console.error('Error importing theme:', error);
        return new Response(JSON.stringify({ 
          success: false, 
          error: 'Invalid import data' 
        }), {
          status: 400,
          headers: { ...headers, 'Content-Type': 'application/json' }
        });
      }
    }
    
    // GET /api/themes/stats - Get theme statistics
    if (url.pathname === '/api/themes/stats' && req.method === 'GET') {
      const result = await getThemeStats();
      return new Response(JSON.stringify(result), {
        headers: { ...headers, 'Content-Type': 'application/json' }
      });
    }
    
    // WebSocket upgrade
    if (url.pathname === '/stream') {
      const success = server.upgrade(req);
      if (success) {
        return undefined;
      }
    }
    
    // Default response
    return new Response('Multi-Agent Observability Server', {
      headers: { ...headers, 'Content-Type': 'text/plain' }
    });
  },
  
  websocket: {
    open(ws) {
      console.log('WebSocket client connected');
      wsClients.add(ws);
      metrics.websocket_connections_total++;
      metrics.websocket_connections_active = wsClients.size;

      // Send recent events on connection
      const events = getRecentEvents(50);
      ws.send(JSON.stringify({ type: 'initial', data: events }));
    },

    message(ws, message) {
      // Handle any client messages if needed
      console.log('Received message:', message);
    },

    close(ws) {
      console.log('WebSocket client disconnected');
      wsClients.delete(ws);
      metrics.websocket_disconnections_total++;
      metrics.websocket_connections_active = wsClients.size;
    },

    error(ws, error) {
      console.error('WebSocket error:', error);
      wsClients.delete(ws);
      metrics.websocket_disconnections_total++;
      metrics.websocket_connections_active = wsClients.size;
    }
  }
});

console.log(`🚀 Server running on http://localhost:${server.port}`);
console.log(`📊 WebSocket endpoint: ws://localhost:${server.port}/stream`);
console.log(`📮 POST events to: http://localhost:${server.port}/events`);