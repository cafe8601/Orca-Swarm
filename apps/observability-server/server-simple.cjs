const http = require('http');
const { WebSocketServer } = require('ws');

const PORT = 4000;

// Create HTTP server
const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Health endpoint
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'ok', 
      timestamp: new Date().toISOString() 
    }));
    return;
  }

  // Default response
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Observability Server Running' }));
});

// Create WebSocket server
const wss = new WebSocketServer({ 
  server,
  path: '/stream'
});

console.log('🚀 Starting WebSocket server on /stream...');

wss.on('connection', (ws) => {
  console.log('✅ WebSocket client connected');

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    message: 'Connected to Observability Server',
    timestamp: new Date().toISOString()
  }));

  // Send periodic updates
  const interval = setInterval(() => {
    if (ws.readyState === 1) { // OPEN
      ws.send(JSON.stringify({
        type: 'update',
        data: {
          timestamp: new Date().toISOString(),
          agents: Math.floor(Math.random() * 5),
          tasks: Math.floor(Math.random() * 100)
        }
      }));
    }
  }, 3000);

  ws.on('message', (data) => {
    console.log('📨 Received:', data.toString());
  });

  ws.on('close', () => {
    console.log('❌ WebSocket client disconnected');
    clearInterval(interval);
  });

  ws.on('error', (error) => {
    console.error('⚠️ WebSocket error:', error.message);
    clearInterval(interval);
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 Observability server running at http://localhost:${PORT}`);
  console.log(`📡 WebSocket endpoint: ws://localhost:${PORT}/stream`);
  console.log(`🏥 Health check: http://localhost:${PORT}/health`);
  console.log('');
  console.log('Ready for connections! 🎉');
});

process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down...');
  process.exit(0);
});
