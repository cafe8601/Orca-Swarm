# 🎤 음성 모드 사용법 (중요!)

## ⚠️ 왜 음성 인식이 안되나요?

### 문제: 백그라운드 실행은 마이크 입력 불가

**음성 모드는 반드시 포그라운드(foreground)에서 실행해야 합니다!**

❌ **안되는 방법** (백그라운드):
```bash
python -m big_three_realtime_agents.main --voice &
# 마이크 입력을 받을 수 없음!
```

✅ **되는 방법** (포그라운드):
```bash
python -m big_three_realtime_agents.main --voice
# 터미널이 마이크 입력 대기
```

---

## 🎯 올바른 사용 방법

### 1단계: 새 터미널 열기
**Command + T** (새 탭) 또는 **새 터미널 창**

### 2단계: 실행
```bash
cd /Users/seohun/Documents/에이전트/infiniteAgent/-multi-agent-learning
source .venv/bin/activate
cd apps/realtime_poc
python -m big_three_realtime_agents.main --voice
```

### 3단계: 마이크 대기 확인
다음 메시지가 나오면:
```
Audio input mode active. Speak into your microphone
```

### 4단계: 말하기
마이크에 대고 명확하게:
- "안녕하세요"
- "파이썬으로 웹 서버 만들어주세요"
- "리액트로 투두 앱 만들어주세요"

### 5단계: 대시보드 확인
다른 브라우저 탭에서:
```
http://localhost:5173
```

---

## 🔧 음성 인식이 안되는 경우

### 체크리스트:
1. ✅ venv 활성화 했나요?
2. ✅ 포그라운드에서 실행 중인가요? (백그라운드 & 아님)
3. ✅ 마이크 권한이 있나요?
4. ✅ 마이크가 작동하나요? (System Preferences → Sound → Input)

### macOS 마이크 권한 확인
```
System Settings 
→ Privacy & Security  
→ Microphone
→ Terminal 체크
```

---

## 💡 더 쉬운 방법: 텍스트 모드 사용

음성이 복잡하면 **텍스트 모드**를 추천합니다:

```bash
python -m big_three_realtime_agents.main --prompt "Create a todo app"
```

**장점**:
- 백그라운드 실행 가능
- 권한 문제 없음  
- 더 빠름
- 똑같은 기능!

---

## 🎯 음성 vs 텍스트 비교

| 기능 | 음성 모드 | 텍스트 모드 |
|------|----------|------------|
| AI 작업 수행 | ✅ | ✅ |
| 코드 생성 | ✅ | ✅ |
| 브라우저 자동화 | ✅ | ✅ |
| Dashboard 모니터링 | ✅ | ✅ |
| 백그라운드 실행 | ❌ | ✅ |
| 권한 필요 | ⚠️ 필요 | ✅ 불필요 |
| 설정 난이도 | 🔴 복잡 | 🟢 쉬움 |

**권장**: 처음에는 **텍스트 모드** 사용!

---

**Made with ❤️ by Multi-Agent Learning System**
