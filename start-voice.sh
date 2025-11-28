#!/bin/bash

echo "🎤 Big Three Agents - 음성 모드 시작"
echo "================================================"
echo ""

PROJECT_ROOT="/Users/seohun/Documents/에이전트/infiniteAgent/-multi-agent-learning"

cd "$PROJECT_ROOT/apps/realtime_poc"
source ../../.venv/bin/activate

echo "✅ 마이크: MacBook Pro 마이크"
echo "✅ 스피커: MacBook Pro 스피커"
echo ""
echo "📊 대시보드에서 실시간 확인:"
echo "   http://localhost:5173"
echo ""
echo "💬 마이크에 대고 말씀하세요!"
echo "   예: '파이썬으로 웹 서버 만들어줘'"
echo ""
echo "================================================"
echo ""

python -m big_three_realtime_agents.main --voice
