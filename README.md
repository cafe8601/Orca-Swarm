# Multi-Agent Learning System v5.0

**자율적 멀티에이전트 오케스트레이션 시스템**

사용자 요청(텍스트/음성)을 받아 AI 에이전트들이 협업하여 자율적으로 작업을 완료합니다.

---

## 시스템 개요

```
[사용자 요청] → [OpenAI Orchestrator] → [전문 에이전트들] → [작업 완료]
       ↑                                                    ↓
       └──────────────── [결과 보고] ←─────────────────────┘
```

### 핵심 구성

| 구성 요소 | 역할 | 기술 |
|-----------|------|------|
| **OpenAI Realtime Voice Agent** | 오케스트레이터 (지휘자) | OpenAI Realtime API, WebSocket |
| **Claude Agentic Coder** | 코드 작성/수정 | Claude API / Claude Max |
| **Gemini Browser Agent** | 웹 브라우저 자동화 | Gemini API, Playwright |
| **Agent Pool** | 154개 전문가 에이전트 | Markdown 정의, 동적 로딩 |

---

## 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 복제 후 디렉토리 이동
cd "multiagent v4 - all"

# Python 가상환경 생성 (3.10+ 권장)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (Gemini Browser Agent용)
playwright install chromium
```

### 2. API 키 설정

```bash
# .env 파일 생성
cp .env.sample .env

# .env 파일 편집하여 API 키 설정
```

**권장 설정 (최소 비용):**

| 서비스 | 설정 | 비용 |
|--------|------|------|
| **Claude Agent SDK** | Claude Max 구독 사용 | **무료** |
| **OpenAI/Gemini** | OpenRouter 사용 | 저렴 |

```bash
# .env 예시 (Claude Max + OpenRouter)
CLAUDE_MODE=max
ANTHROPIC_API_KEY=              # 비워두기 - Claude Max 자동 사용

OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENAI_API_KEY=sk-or-v1-xxxxx   # OpenRouter 키와 동일
OPENAI_BASE_URL=https://openrouter.ai/api/v1
GEMINI_API_KEY=sk-or-v1-xxxxx   # OpenRouter 키와 동일
```

**API 키 획득:**
- OpenRouter: https://openrouter.ai/keys (OpenAI, Gemini 등 통합)

### 3. 실행

```bash
# 간편 실행 (메뉴 방식)
./START_HERE.sh

# 또는 직접 실행
cd apps/realtime_poc
python -m big_three_realtime_agents.main
```

---

## 실행 모드

### 음성 모드
```bash
python -m big_three_realtime_agents.main --voice
```
마이크로 자연어 명령을 내립니다.

### 텍스트 모드
```bash
python -m big_three_realtime_agents.main
```
키보드로 명령을 입력합니다.

### 자동 프롬프트 모드
```bash
python -m big_three_realtime_agents.main --prompt "웹사이트를 만들어줘"
```
단일 명령을 자동 실행합니다.

### 옵션
```bash
--input text|audio    # 입력 모드
--output text|audio   # 출력 모드
--mini               # 경량 모델 사용
--timeout 300        # 타임아웃 (초)
```

---

## 프로젝트 구조

```
multiagent v4 - all/
├── apps/
│   ├── realtime_poc/              # Big Three 에이전트 (메인)
│   │   ├── big_three_realtime_agents/
│   │   │   ├── main.py            # 진입점
│   │   │   ├── agents/            # 에이전트 모듈들
│   │   │   │   ├── openai/        # 오케스트레이터
│   │   │   │   ├── claude/        # 코딩 에이전트
│   │   │   │   ├── gemini/        # 브라우저 에이전트
│   │   │   │   └── pool/          # 에이전트 풀
│   │   │   ├── memory/            # 메모리 시스템
│   │   │   ├── learning/          # 학습 시스템
│   │   │   ├── workflow/          # 워크플로우
│   │   │   └── security/          # 보안
│   │   └── ...
│   │
│   ├── observability-server/       # 모니터링 서버
│   └── observability-client/       # 대시보드 UI
│
├── agentpool/                      # 154개 에이전트 정의
│   ├── agents-tier1-core/          # Tier 1: 핵심 (20개)
│   ├── agents-tier2-specialized/   # Tier 2: 전문 (120개)
│   └── agents-tier3-experimental/  # Tier 3: 실험 (14개)
│
├── monitoring/                     # Docker 모니터링 스택
│
├── START_HERE.sh                   # 간편 실행 스크립트
├── RUN_ME.sh                       # 대체 실행 스크립트
├── setup.sh                        # 환경 설정 스크립트
├── .env.sample                     # 환경 변수 템플릿
└── requirements.txt                # Python 의존성
```

---

## 에이전트 풀 (154개)

### Tier 1: Core (20개) - 프로덕션 검증 완료
- backend-developer, frontend-developer
- python-pro, devops-engineer
- qa-expert, security-auditor
- 등...

### Tier 2: Specialized (~120개) - 전문 분야
- **Languages**: Rust, Go, Java, Kotlin, Scala...
- **Frameworks**: Next.js, Django, Rails, Laravel...
- **Infrastructure**: Terraform, K8s, SRE...
- **Quality**: Testing, Performance...
- **Security**: Penetration, Compliance...
- **Data/AI**: MLOps, Data Science...

### Tier 3: Experimental (~14개) - 실험적
- Blockchain, Gaming, Emerging Tech...

---

## 사용 예시

### 예시 1: 웹 앱 개발
```
사용자: "Python으로 할 일 관리 앱을 만들어줘"

시스템 동작:
1. [오케스트레이터] 요청 분석 → 코딩 작업으로 판단
2. [Claude Agent] 프로젝트 구조 설계
3. [Claude Agent] 코드 파일 생성
4. [Claude Agent] 테스트 코드 작성
5. [오케스트레이터] 결과 통합 및 보고

결과: apps/content-gen/ 디렉토리에 완성된 앱
```

### 예시 2: 웹 리서치
```
사용자: "최신 AI 트렌드를 조사해줘"

시스템 동작:
1. [오케스트레이터] 요청 분석 → 브라우저 작업으로 판단
2. [Gemini Browser] 검색 엔진 접속
3. [Gemini Browser] 관련 기사/논문 수집
4. [오케스트레이터] 결과 요약 및 보고
```

---

## 모니터링 대시보드

```bash
# 대시보드 시작
cd apps/observability-server
node server-simple.cjs &

cd ../observability-client
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

---

## 문제 해결

### 일반적인 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `OPENAI_API_KEY not set` | 환경 변수 누락 | `.env` 파일 확인 |
| `playwright not found` | 의존성 미설치 | `pip install playwright && playwright install` |
| `WebSocket connection failed` | 네트워크 문제 | 인터넷 연결 확인 |
| `Agent timeout` | 작업 시간 초과 | `--timeout` 값 증가 |

### 로그 확인
```bash
tail -f apps/realtime_poc/logs/agent.log
```

---

## 라이선스

MIT License

---

## 참고 문서

- [시스템 상세 가이드](MULTIAGENT_SYSTEM_GUIDE.md)
- [작동 원리 시각화](multi-agent-system-v5-how-it-works.html)
