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
echo "4) 📋 프로파일/워크플로우 목록"
echo "5) 🛑 전체 종료"
echo ""
read -p "선택 (1-5): " choice

# Function to select profile
select_profile() {
    echo ""
    echo "🔧 프로파일 선택:"
    echo "  1) 👨‍💻 Developer - 소프트웨어 개발"
    echo "  2) 📚 Researcher - 학술 연구/논문 작성"
    echo "  3) 📊 Business - 비즈니스 분석/전략"
    echo ""
    read -p "프로파일 선택 (1-3, 기본: 1): " profile_choice

    case $profile_choice in
        2)
            PROFILE="researcher"
            ;;
        3)
            PROFILE="business"
            ;;
        *)
            PROFILE="developer"
            ;;
    esac
    echo "✅ 프로파일: $PROFILE"
}

# Function to start observability
start_observability() {
    cd apps/observability-server
    nohup node server-simple.cjs > /tmp/obs-server.log 2>&1 &
    cd ../observability-client
    nohup npm run dev > /tmp/obs-client.log 2>&1 &
    sleep 3
}

case $choice in
  1)
    select_profile
    echo ""
    echo "🎤 음성 모드 시작..."
    echo "📊 대시보드: http://localhost:5173"
    echo ""

    # Observability 시작
    start_observability

    # Big Three 음성 모드
    cd ../realtime_poc
    source ../../.venv/bin/activate
    python -m big_three_realtime_agents.main --voice --profile "$PROFILE"
    ;;

  2)
    select_profile
    echo ""

    # 워크플로우 선택 (선택사항)
    echo "📋 워크플로우를 선택하시겠습니까? (선택사항)"
    echo "  1) 없음 (자유 모드)"

    if [ "$PROFILE" == "developer" ]; then
        echo "  2) feature_development - 기능 개발"
        echo "  3) bug_fix - 버그 수정"
        echo "  4) code_review - 코드 리뷰"
        echo "  5) refactoring - 리팩토링"
    elif [ "$PROFILE" == "researcher" ]; then
        echo "  2) literature_review - 문헌 검토"
        echo "  3) paper_writing - 논문 작성"
        echo "  4) technical_report - 기술 보고서"
    elif [ "$PROFILE" == "business" ]; then
        echo "  2) market_analysis - 시장 분석"
        echo "  3) strategic_plan - 전략 기획"
        echo "  4) business_report - 비즈니스 보고서"
        echo "  5) swot_analysis - SWOT 분석"
    fi

    echo ""
    read -p "워크플로우 선택 (1-5, 기본: 1): " workflow_choice

    WORKFLOW=""
    if [ "$PROFILE" == "developer" ]; then
        case $workflow_choice in
            2) WORKFLOW="feature_development";;
            3) WORKFLOW="bug_fix";;
            4) WORKFLOW="code_review";;
            5) WORKFLOW="refactoring";;
        esac
    elif [ "$PROFILE" == "researcher" ]; then
        case $workflow_choice in
            2) WORKFLOW="literature_review";;
            3) WORKFLOW="paper_writing";;
            4) WORKFLOW="technical_report";;
        esac
    elif [ "$PROFILE" == "business" ]; then
        case $workflow_choice in
            2) WORKFLOW="market_analysis";;
            3) WORKFLOW="strategic_plan";;
            4) WORKFLOW="business_report";;
            5) WORKFLOW="swot_analysis";;
        esac
    fi

    read -p "💬 명령을 입력하세요: " prompt
    echo ""
    echo "⚙️  실행 중..."

    # Observability 시작
    start_observability

    # Big Three 텍스트 모드
    cd ../realtime_poc
    source ../../.venv/bin/activate

    if [ -n "$WORKFLOW" ]; then
        python -m big_three_realtime_agents.main --prompt "$prompt" --timeout 120 --profile "$PROFILE" --workflow "$WORKFLOW"
    else
        python -m big_three_realtime_agents.main --prompt "$prompt" --timeout 120 --profile "$PROFILE"
    fi
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
    echo "📋 프로파일 및 워크플로우 목록"
    echo ""

    cd apps/realtime_poc
    source ../../.venv/bin/activate

    echo "=== 사용 가능한 프로파일 ==="
    python -m big_three_realtime_agents.main --list-profiles

    echo ""
    echo "=== 사용 가능한 워크플로우 ==="
    python -m big_three_realtime_agents.main --list-workflows
    ;;

  5)
    echo ""
    echo "🛑 모든 서비스 종료 중..."
    pkill -f "big_three\|observability\|vite\|server-simple" 2>/dev/null
    echo "✅ 종료 완료"
    ;;

  *)
    echo "잘못된 선택입니다"
    ;;
esac
