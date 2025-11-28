#!/bin/bash

echo "🚀 Multi-Agent Learning System - 전체 시작"
echo "================================================"
echo ""

# 프로젝트 루트
PROJECT_ROOT="/Users/seohun/Documents/에이전트/infiniteAgent/-multi-agent-learning"

# 1. Observability Server 시작 (Background)
echo "1️⃣  Observability Server 시작 중... (Port 4000)"
cd "$PROJECT_ROOT/apps/observability-server"
nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
SERVER_PID=$!
echo "   ✅ Server PID: $SERVER_PID"
sleep 2

# 2. Observability Client 시작 (Background)
echo ""
echo "2️⃣  Observability Client 시작 중... (Port 5173)"
cd "$PROJECT_ROOT/apps/observability-client"
nohup npm run dev > /tmp/obs-client.log 2>&1 &
CLIENT_PID=$!
echo "   ✅ Client PID: $CLIENT_PID"
sleep 3

# 3. 서비스 확인
echo ""
echo "3️⃣  서비스 상태 확인..."
if lsof -i :4000 > /dev/null 2>&1; then
    echo "   ✅ Server running on port 4000"
else
    echo "   ❌ Server failed to start"
fi

if lsof -i :5173 > /dev/null 2>&1; then
    echo "   ✅ Client running on port 5173"
else
    echo "   ❌ Client failed to start"
fi

echo ""
echo "================================================"
echo "✅ Observability Dashboard 실행 완료!"
echo ""
echo "📊 Dashboard: http://localhost:5173"
echo "🔧 Server: http://localhost:4000/health"
echo ""
echo "📝 로그 보기:"
echo "   Server: tail -f /tmp/obs-server.log"
echo "   Client: tail -f /tmp/obs-client.log"
echo ""
echo "🛑 종료하기:"
echo "   kill $SERVER_PID $CLIENT_PID"
echo ""
echo "================================================"
echo ""
echo "🎤 Big Three Agents를 시작하려면:"
echo "   cd apps/realtime_poc && source ../../.venv/bin/activate"
echo "   python -m big_three_realtime_agents.main --voice"
echo ""
