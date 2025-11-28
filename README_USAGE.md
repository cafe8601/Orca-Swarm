# 🚀 Multi-Agent Learning System - 사용 가이드

## ⚡ 빠른 시작

### 가장 간단한 방법
```bash
./START_HERE.sh
```

메뉴에서 선택하세요:
- `1` - 🎤 음성 모드
- `2` - ⌨️  텍스트 모드
- `3` - 📊 대시보드만
- `4` - 🛑 종료

---

## 🎤 음성 모드 사용법

### 1. 시작
```bash
./START_HERE.sh
1 선택
```

### 2. 마이크에 대고 말하기
- "파이썬으로 웹 서버 만들어줘"
- "리액트로 투두 앱 만들어줘"
- "이 코드 테스트해줘"

### 3. 실시간 확인
브라우저: http://localhost:5173

### 4. 조작
- **SHIFT + SPACE**: 일시정지/재개
- **Ctrl + C**: 종료

---

## ⌨️  텍스트 모드 사용법

### 한 줄 명령
```bash
cd apps/realtime_poc
source ../../.venv/bin/activate
python -m big_three_realtime_agents.main --prompt "Create a todo app"
```

### 대화형
```bash
python -m big_three_realtime_agents.main
> 명령 입력
```

---

## 📊 결과 확인

### 생성된 파일 위치
```bash
apps/content-gen/backend/     # 백엔드 코드
apps/content-gen/frontend/    # 프론트엔드 코드
apps/content-gen/agents/      # 에이전트 세션
```

### 로그 확인
```bash
tail -f apps/realtime_poc/output_logs/*.log
```

---

## 🛠️ 문제 해결

### pyaudio 오류
```bash
source .venv/bin/activate  # 가상환경 활성화 필수!
```

### 포트 충돌
```bash
pkill -f "big_three\|observability"  # 기존 프로세스 종료
```

---

## 🎯 예시 작업

### 웹 앱 만들기
```
"Create a FastAPI backend with SQLite database"
"Add user authentication with JWT"
"Create React frontend"
```

### 브라우저 테스트
```
"Test the login form at localhost:3000"
"Navigate to google.com and search"
```

### 코드 개선
```
"Optimize this code for performance"
"Add comprehensive tests"
"Refactor using best practices"
```

---

**Made with ❤️ by Multi-Agent Learning System**
