#!/bin/bash
# Start Big Three Agents Observability System

set -e

echo "🚀 Starting Big Three Multi-Agent Observability System..."
echo "========================================================="

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker compose &> /dev/null; then
    echo "🐳 Docker detected - using Docker Compose"
    echo ""
    echo "Starting observability services..."
    docker compose up -d observability-server observability-client
    
    echo ""
    echo "✅ Observability system started!"
    echo "   📊 Dashboard: http://localhost:5173"
    echo "   🔌 Server API: http://localhost:4000"
    echo "   📡 WebSocket: ws://localhost:4000"
    echo ""
    echo "View logs:"
    echo "   docker compose logs -f observability-server"
    echo "   docker compose logs -f observability-client"
    echo ""
    echo "Stop services:"
    echo "   docker compose stop observability-server observability-client"
    
else
    echo "📦 Docker not found - using native installation"
    
    # Check if bun is installed
    if ! command -v bun &> /dev/null; then
        echo "❌ Bun is not installed. Please install it from https://bun.sh"
        echo "   Or use Docker: docker compose up -d observability-server observability-client"
        exit 1
    fi
    
    # Start server
    cd apps/observability-server
    echo "📦 Installing server dependencies..."
    bun install
    echo "🖥️  Starting server on port 4000..."
    bun run src/index.ts &
    SERVER_PID=$!
    
    # Wait for server
    sleep 3
    
    # Start client
    cd ../observability-client
    echo "📦 Installing client dependencies..."
    bun install
    echo "🌐 Starting client on port 5173..."
    bun run dev &
    CLIENT_PID=$!
    
    echo ""
    echo "✅ Observability system started!"
    echo "   📊 Dashboard: http://localhost:5173"
    echo "   🔌 Server: http://localhost:4000"
    echo ""
    echo "Press Ctrl+C to stop both services"
    
    # Cleanup on exit
    trap "kill $SERVER_PID $CLIENT_PID 2>/dev/null" EXIT
    
    wait
fi
