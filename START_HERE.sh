#!/bin/bash

clear
echo "🎉 Multi-Agent Learning System"
echo "======================================"
echo ""
echo "🎯 무엇을 하시겠습니까?"
echo ""
echo "1) 🎤 음성 모드 (마이크로 명령)"
echo "2) ⌨️  텍스트 모드 (타이핑으로 명령)"
echo "3) 📊 대시보드만 보기"
echo "4) 🛑 전체 종료"
echo ""
read -p "선택 (1-4): " choice

case $choice in
  1)
    echo ""
    echo "🎤 음성 모드 시작..."
    echo "📊 대시보드: http://localhost:5173"
    echo ""
    
    # Observability 시작
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client
    nohup npm run dev > /tmp/obs-client.log 2>&1 &
    sleep 3
    
    # Big Three 음성 모드
    cd ../realtime_poc
    source ../../.venv/bin/activate
    python -m big_three_realtime_agents.main --voice
    ;;
    
  2)
    echo ""
    read -p "💬 명령을 입력하세요: " prompt
    echo ""
    echo "⚙️  실행 중..."
    
    # Observability 시작
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client  
    nohup npm run dev > /tmp/obs-client.log 2>&1 &
    sleep 3
    
    # Big Three 텍스트 모드
    cd ../realtime_poc
    source ../../.venv/bin/activate
    python -m big_three_realtime_agents.main --prompt "$prompt" --timeout 120
    ;;
    
  3)
    echo ""
    echo "📊 대시보드만 시작..."
    
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client
    npm run dev
    ;;
    
  4)
    echo ""
    echo "🛑 모든 서비스 종료 중..."
    pkill -f "big_three\|observability\|vite\|server-simple" 2>/dev/null
    echo "✅ 종료 완료"
    ;;
    
  *)
    echo "잘못된 선택입니다"
    ;;
esac
