#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}🚀 Multi-Agent Learning System${NC}"
echo "======================================"
echo ""

# 현재 환경 확인
current_env=$(basename "$CONDA_DEFAULT_ENV" 2>/dev/null || echo "none")
if [ "$current_env" != "none" ] && [ "$current_env" != "base" ]; then
    echo -e "${YELLOW}⚠️  Conda 환경 감지: $current_env${NC}"
    echo -e "${YELLOW}   venv로 전환합니다...${NC}"
    conda deactivate 2>/dev/null
    echo ""
fi

# 프로젝트 루트로 이동
cd /Users/seohun/Documents/에이전트/infiniteAgent/-multi-agent-learning

# venv 활성화 체크
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ .venv가 없습니다!${NC}"
    exit 1
fi

# 항상 venv 활성화
source .venv/bin/activate
echo -e "${GREEN}✅ 가상환경 활성화됨 (.venv)${NC}"
echo ""

# Python 버전 확인
python_version=$(python --version)
echo "🐍 Python: $python_version"
echo ""

# 메뉴
echo -e "${BLUE}무엇을 하시겠습니까?${NC}"
echo ""
echo "1) 🎤 음성 모드 (마이크로 명령)"
echo "2) ⌨️  텍스트 모드 (한 줄 명령)"
echo "3) 💬 대화형 모드 (계속 대화)"
echo "4) 📊 대시보드만 시작"
echo "5) 🛑 전체 종료"
echo ""
read -p "선택 (1-5): " choice
echo ""

case $choice in
  1)
    echo -e "${GREEN}🎤 음성 모드 시작...${NC}"
    echo ""
    echo "📊 대시보드: http://localhost:5173"
    echo "🎙️  마이크에 대고 말씀하세요!"
    echo ""
    
    # Observability 시작
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client
    nohup npm run dev > /tmp/obs-client.log 2>&1 &
    sleep 3
    
    # Big Three 음성 모드
    cd ../realtime_poc
    python -m big_three_realtime_agents.main --voice
    ;;
    
  2)
    echo -e "${BLUE}⌨️  텍스트 모드${NC}"
    read -p "💬 명령을 입력하세요: " prompt
    echo ""
    
    # Observability 시작
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client
    nohup npm run dev > /tmp/obs-client.log 2>&1 &
    sleep 3
    
    # Big Three 실행
    cd ../realtime_poc
    echo -e "${GREEN}⚙️  실행 중...${NC}"
    python -m big_three_realtime_agents.main --prompt "$prompt" --timeout 120
    ;;
    
  3)
    echo -e "${BLUE}💬 대화형 모드${NC}"
    echo ""
    
    # Observability 시작
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client
    nohup npm run dev > /tmp/obs-client.log 2>&1 &
    sleep 3
    
    # Big Three 대화형
    cd ../realtime_poc
    python -m big_three_realtime_agents.main
    ;;
    
  4)
    echo -e "${BLUE}📊 대시보드만 시작...${NC}"
    
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client
    npm run dev
    ;;
    
  5)
    echo -e "${YELLOW}🛑 모든 서비스 종료 중...${NC}"
    pkill -f "big_three\|observability\|vite\|server-simple" 2>/dev/null
    echo -e "${GREEN}✅ 종료 완료${NC}"
    ;;
    
  *)
    echo -e "${RED}❌ 잘못된 선택입니다${NC}"
    ;;
esac
