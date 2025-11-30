# Big Three Realtime Agents 사용자 가이드북

**버전**: 1.0
**최종 업데이트**: 2024년 11월

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [설치 및 초기 설정](#2-설치-및-초기-설정)
3. [기본 사용법](#3-기본-사용법)
4. [프로파일 시스템](#4-프로파일-시스템)
5. [워크플로우 활용](#5-워크플로우-활용)
6. [실전 예제](#6-실전-예제)
7. [고급 기능](#7-고급-기능)
8. [문제 해결](#8-문제-해결)
9. [부록](#9-부록)

---

## 1. 시스템 개요

### 1.1 Big Three란?

Big Three Realtime Agents는 세 가지 핵심 AI 에이전트를 통합한 멀티에이전트 시스템입니다:

| 에이전트 | 역할 | 주요 기능 |
|---------|------|----------|
| **OpenAI Realtime** | 오케스트레이터 | 음성/텍스트 대화, 작업 분배 |
| **Claude Code** | 코드 전문가 | 코드 작성, 분석, 리팩토링 |
| **Gemini Browser** | 웹 자동화 | 브라우저 제어, 웹 검색, 스크린샷 |

### 1.2 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 (음성/텍스트)                     │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenAI Realtime Voice Agent                    │
│                    (메인 오케스트레이터)                      │
│  • 사용자 의도 파악                                          │
│  • 작업 분해 및 할당                                         │
│  • 결과 통합 및 응답                                         │
└────────┬────────────────────┬────────────────────┬──────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────────┐
│ Claude Code │      │   Gemini    │      │   Agent Pool    │
│   Agent     │      │   Browser   │      │  (154 전문가)    │
├─────────────┤      ├─────────────┤      ├─────────────────┤
│ • 코드 생성  │      │ • 웹 검색   │      │ • 특화 분석     │
│ • 버그 수정  │      │ • 폼 작성   │      │ • 도메인 전문성  │
│ • 리팩토링   │      │ • 스크린샷  │      │ • 다중 관점     │
└─────────────┘      └─────────────┘      └─────────────────┘
```

### 1.3 Agent Pool 구성

154개의 전문 에이전트가 3개 티어로 구성됩니다:

| 티어 | 에이전트 수 | 특징 | 예시 |
|-----|-----------|------|------|
| **Core** | 15개 | 핵심 분석 역량 | system-architect, security-auditor |
| **Specialized** | 50개+ | 도메인 전문성 | react-expert, database-optimizer |
| **Experimental** | 89개+ | 실험적 기능 | ml-pipeline-designer |

---

## 2. 설치 및 초기 설정

### 2.1 시스템 요구사항

| 항목 | 최소 사양 | 권장 사양 |
|-----|----------|----------|
| Python | 3.11+ | 3.12 |
| RAM | 8GB | 16GB |
| 저장공간 | 5GB | 10GB |
| OS | Linux/macOS/WSL2 | Ubuntu 22.04+ |

### 2.2 자동 설치 (권장)

```bash
# 1. 프로젝트 디렉토리 이동
cd "/home/cafe99/MAS_proj/multiagent v4 - all"

# 2. 설치 스크립트 실행
chmod +x setup.sh
./setup.sh
```

설치 스크립트가 자동으로 수행하는 작업:
- ✅ Python 버전 확인
- ✅ 가상환경 생성 (`.venv`)
- ✅ 의존성 설치 (`requirements.txt`)
- ✅ Playwright 브라우저 설치
- ✅ 환경 설정 파일 생성 (`.env`)
- ✅ 저장 디렉토리 생성

### 2.3 API 키 설정

설치 후 `.env` 파일을 편집하여 API 키를 설정합니다:

```bash
# .env 파일 편집
nano .env
```

필수 API 키:
```env
# OpenAI (필수) - 메인 오케스트레이터
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Gemini (필수) - 브라우저 자동화
GEMINI_API_KEY=your-gemini-key-here

# Anthropic (선택) - Claude Code Agent
# API 키 없으면 Claude Max 브라우저 모드 사용
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 2.4 설치 확인

```bash
# 가상환경 활성화
source .venv/bin/activate

# 프로파일 목록 확인
python -m big_three_realtime_agents.main --list-profiles

# 워크플로우 목록 확인
python -m big_three_realtime_agents.main --list-workflows
```

---

## 3. 기본 사용법

### 3.1 대화형 런처 (START_HERE.sh)

가장 쉬운 시작 방법입니다:

```bash
cd "/home/cafe99/MAS_proj/multiagent v4 - all/apps"
./START_HERE.sh
```

메뉴가 표시됩니다:
```
🎉 Multi-Agent Learning System
======================================

🎯 무엇을 하시겠습니까?

1) 🎤 음성 모드 (마이크로 명령)
2) ⌨️  텍스트 모드 (타이핑으로 명령)
3) 📊 대시보드만 보기
4) 📋 프로파일/워크플로우 목록
5) 🛑 전체 종료

선택 (1-5):
```

### 3.2 명령줄 직접 실행

#### 텍스트 모드 (기본)
```bash
cd "/home/cafe99/MAS_proj/multiagent v4 - all/apps/realtime_poc"
source ../../.venv/bin/activate

# 기본 실행
python -m big_three_realtime_agents.main

# 프롬프트와 함께 실행
python -m big_three_realtime_agents.main --prompt "Hello, what can you do?"
```

#### 음성 모드
```bash
# 음성 입력 + 음성 출력
python -m big_three_realtime_agents.main --voice

# 음성 입력 + 텍스트 출력
python -m big_three_realtime_agents.main --input audio --output text

# 텍스트 입력 + 음성 출력
python -m big_three_realtime_agents.main --input text --output audio
```

### 3.3 명령줄 옵션 정리

| 옵션 | 설명 | 기본값 |
|-----|------|-------|
| `--input` | 입력 모드 (text/audio) | text |
| `--output` | 출력 모드 (text/audio) | text |
| `--voice` | 음성 모드 활성화 | - |
| `--prompt` | 자동 실행할 프롬프트 | - |
| `--profile` | 사용할 프로파일 | developer |
| `--workflow` | 실행할 워크플로우 | - |
| `--mini` | 경량 모델 사용 | - |
| `--timeout` | 자동 프롬프트 타임아웃(초) | 300 |
| `--list-profiles` | 프로파일 목록 표시 | - |
| `--list-workflows` | 워크플로우 목록 표시 | - |

---

## 4. 프로파일 시스템

### 4.1 프로파일이란?

프로파일은 특정 작업 유형에 최적화된 시스템 설정입니다. 각 프로파일은:
- 시스템 프롬프트 조정
- 우선 에이전트 선택
- 관련 워크플로우 활성화

### 4.2 기본 제공 프로파일

#### 👨‍💻 Developer (개발자)

소프트웨어 개발에 최적화된 프로파일입니다.

```bash
python -m big_three_realtime_agents.main --profile developer
```

**주요 에이전트**: system-architect, code-reviewer, test-engineer
**주요 워크플로우**: feature_development, bug_fix, code_review, refactoring

**적합한 작업**:
- 새로운 기능 구현
- 버그 수정 및 디버깅
- 코드 리뷰 및 품질 개선
- 리팩토링 및 최적화

#### 📚 Researcher (연구자)

학술 연구 및 논문 작성에 최적화된 프로파일입니다.

```bash
python -m big_three_realtime_agents.main --profile researcher
```

**주요 에이전트**: research-analyst, data-scientist, technical-writer
**주요 워크플로우**: literature_review, paper_writing, technical_report

**적합한 작업**:
- 문헌 조사 및 분석
- 논문 작성 지원
- 데이터 분석 및 시각화
- 기술 보고서 작성

#### 📊 Business (비즈니스)

비즈니스 분석 및 전략 기획에 최적화된 프로파일입니다.

```bash
python -m big_three_realtime_agents.main --profile business
```

**주요 에이전트**: business-analyst, market-researcher, strategy-consultant
**주요 워크플로우**: market_analysis, strategic_plan, business_report, swot_analysis

**적합한 작업**:
- 시장 분석 및 경쟁사 조사
- 전략 기획 및 사업 계획
- SWOT/PEST 분석
- 비즈니스 보고서 작성

---

## 5. 워크플로우 활용

### 5.1 워크플로우란?

워크플로우는 복잡한 작업을 단계별로 안내하는 템플릿입니다.

### 5.2 Developer 워크플로우

#### feature_development (기능 개발)
```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow feature_development \
  --prompt "사용자 인증 시스템을 구현해줘"
```

**실행 단계**:
1. 요구사항 분석
2. 설계 및 아키텍처 결정
3. 코드 구현
4. 테스트 작성
5. 문서화

#### bug_fix (버그 수정)
```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow bug_fix \
  --prompt "로그인 시 500 에러가 발생해"
```

**실행 단계**:
1. 에러 로그 분석
2. 원인 파악
3. 수정 코드 작성
4. 테스트 검증

#### code_review (코드 리뷰)
```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow code_review \
  --prompt "src/auth 폴더의 코드를 리뷰해줘"
```

**실행 단계**:
1. 코드 구조 분석
2. 품질 이슈 식별
3. 보안 취약점 검사
4. 개선 사항 제안

#### refactoring (리팩토링)
```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow refactoring \
  --prompt "UserService 클래스를 리팩토링해줘"
```

### 5.3 Researcher 워크플로우

#### literature_review (문헌 검토)
```bash
python -m big_three_realtime_agents.main \
  --profile researcher \
  --workflow literature_review \
  --prompt "딥러닝 기반 자연어 처리 최신 연구 동향을 조사해줘"
```

#### paper_writing (논문 작성)
```bash
python -m big_three_realtime_agents.main \
  --profile researcher \
  --workflow paper_writing \
  --prompt "실험 결과를 바탕으로 논문 초안을 작성해줘"
```

#### technical_report (기술 보고서)
```bash
python -m big_three_realtime_agents.main \
  --profile researcher \
  --workflow technical_report \
  --prompt "시스템 성능 테스트 결과 보고서를 작성해줘"
```

### 5.4 Business 워크플로우

#### market_analysis (시장 분석)
```bash
python -m big_three_realtime_agents.main \
  --profile business \
  --workflow market_analysis \
  --prompt "국내 AI SaaS 시장을 분석해줘"
```

#### strategic_plan (전략 기획)
```bash
python -m big_three_realtime_agents.main \
  --profile business \
  --workflow strategic_plan \
  --prompt "2025년 사업 확장 전략을 수립해줘"
```

#### swot_analysis (SWOT 분석)
```bash
python -m big_three_realtime_agents.main \
  --profile business \
  --workflow swot_analysis \
  --prompt "우리 회사의 SWOT 분석을 해줘"
```

#### business_report (비즈니스 보고서)
```bash
python -m big_three_realtime_agents.main \
  --profile business \
  --workflow business_report \
  --prompt "분기별 실적 보고서를 작성해줘"
```

---

## 6. 실전 예제

### 6.1 웹 애플리케이션 개발

#### 예제: React 대시보드 만들기

**시나리오**: 실시간 데이터를 표시하는 관리자 대시보드 개발

```bash
# 1. 기능 개발 워크플로우로 시작
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow feature_development \
  --prompt "React와 Chart.js를 사용해서 실시간 데이터 대시보드를 만들어줘.
  사용자 통계, 매출 그래프, 알림 패널이 필요해."
```

**시스템 동작**:
1. **OpenAI Realtime**: 요구사항 분석 후 작업 분배
2. **Claude Code**: React 컴포넌트 코드 생성
3. **Gemini Browser**: Chart.js 문서 검색, 예제 수집
4. **Agent Pool**: UI/UX 전문가가 레이아웃 제안

#### 예제: API 서버 구축

```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --prompt "FastAPI로 RESTful API 서버를 만들어줘.
  - 사용자 CRUD
  - JWT 인증
  - PostgreSQL 연동
  - Swagger 문서화"
```

### 6.2 버그 수정

#### 예제: 메모리 누수 디버깅

```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow bug_fix \
  --prompt "프로덕션 서버에서 메모리 사용량이 계속 증가해.
  src/services/cache.py 파일이 의심돼."
```

**시스템 동작**:
1. 코드 분석으로 메모리 누수 패턴 탐지
2. 프로파일링 도구 제안
3. 수정 코드 및 테스트 제공

#### 예제: 성능 이슈 해결

```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow bug_fix \
  --prompt "데이터베이스 쿼리가 너무 느려.
  /api/users 엔드포인트가 5초 이상 걸려."
```

### 6.3 코드 리뷰 및 리팩토링

#### 예제: 레거시 코드 현대화

```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow refactoring \
  --prompt "src/legacy 폴더의 코드를 현대적인 Python 스타일로 리팩토링해줘.
  타입 힌트 추가하고, async/await 패턴 적용해줘."
```

#### 예제: 보안 코드 리뷰

```bash
python -m big_three_realtime_agents.main \
  --profile developer \
  --workflow code_review \
  --prompt "src/auth와 src/api 폴더의 보안 취약점을 검사해줘.
  SQL Injection, XSS, CSRF 위험이 있는지 확인해."
```

### 6.4 연구 및 분석

#### 예제: 기술 동향 조사

```bash
python -m big_three_realtime_agents.main \
  --profile researcher \
  --workflow literature_review \
  --prompt "2024년 LLM 에이전트 시스템 연구 동향을 조사해줘.
  주요 논문, 핵심 기술, 한계점을 정리해줘."
```

**시스템 동작**:
1. **Gemini Browser**: arXiv, Google Scholar 검색
2. **Agent Pool**: research-analyst가 논문 분석
3. **Claude Code**: 핵심 내용 요약 및 문서화

#### 예제: 데이터 분석 보고서

```bash
python -m big_three_realtime_agents.main \
  --profile researcher \
  --workflow technical_report \
  --prompt "data/sales_2024.csv 파일을 분석해서
  분기별 매출 동향, 상위 제품, 예측 모델을 포함한 보고서를 만들어줘."
```

### 6.5 비즈니스 분석

#### 예제: 경쟁사 분석

```bash
python -m big_three_realtime_agents.main \
  --profile business \
  --workflow market_analysis \
  --prompt "국내 클라우드 서비스 시장에서 AWS, Azure, GCP의
  점유율, 가격 정책, 강점/약점을 분석해줘."
```

**시스템 동작**:
1. **Gemini Browser**: 각 서비스 웹사이트 방문, 가격표 수집
2. **Agent Pool**: business-analyst가 비교 분석
3. **Claude Code**: 분석 결과를 표/차트로 정리

#### 예제: 사업 계획서 작성

```bash
python -m big_three_realtime_agents.main \
  --profile business \
  --workflow strategic_plan \
  --prompt "AI 기반 고객 서비스 챗봇 스타트업 사업 계획서를 작성해줘.
  시장 분석, 비즈니스 모델, 재무 계획, 마케팅 전략을 포함해줘."
```

### 6.6 음성 대화 세션

#### 예제: 페어 프로그래밍

```bash
# 음성 모드로 실시간 코딩 지원
python -m big_three_realtime_agents.main \
  --voice \
  --profile developer
```

대화 예시:
```
You: "새로운 React 컴포넌트를 만들고 싶어"
AI: "어떤 종류의 컴포넌트가 필요하신가요? 폼, 테이블, 카드 중에서 선택해주세요."
You: "사용자 프로필을 보여주는 카드 컴포넌트"
AI: "알겠습니다. 프로필 카드 컴포넌트를 만들어드릴게요. 이미지, 이름, 이메일, 소개 필드를 포함할까요?"
...
```

#### 예제: 브레인스토밍 세션

```bash
python -m big_three_realtime_agents.main \
  --voice \
  --profile business
```

대화 예시:
```
You: "새로운 제품 아이디어를 브레인스토밍하고 싶어"
AI: "좋습니다! 어떤 산업 분야에 관심이 있으신가요?"
You: "헬스케어 분야"
AI: "헬스케어 분야에서 해결하고 싶은 문제가 있나요? 예를 들어 진단, 모니터링, 환자 관리 중 어떤 영역인가요?"
...
```

---

## 7. 고급 기능

### 7.1 Agent Pool 직접 활용

특정 전문 에이전트를 직접 호출할 수 있습니다:

```bash
python -m big_three_realtime_agents.main \
  --prompt "security-auditor 에이전트를 사용해서
  전체 프로젝트의 보안 취약점을 검사해줘"
```

주요 전문 에이전트:
| 에이전트 ID | 전문 분야 |
|------------|----------|
| `system-architect` | 시스템 설계 |
| `security-auditor` | 보안 감사 |
| `performance-optimizer` | 성능 최적화 |
| `database-expert` | 데이터베이스 설계 |
| `api-designer` | API 설계 |
| `test-engineer` | 테스트 전략 |
| `devops-engineer` | CI/CD, 인프라 |
| `ml-engineer` | 머신러닝 파이프라인 |

### 7.2 경량 모델 사용

비용 절감이 필요할 때:

```bash
# mini 모델 사용 (약 10배 저렴)
python -m big_three_realtime_agents.main \
  --mini \
  --prompt "간단한 Python 함수를 만들어줘"
```

모델 비교:
| 모델 | 텍스트 입력 | 텍스트 출력 | 음성 입력 | 음성 출력 |
|-----|-----------|-----------|---------|---------|
| gpt-realtime-2025-08-28 | $10/1M | $40/1M | $200/1M | $800/1M |
| gpt-realtime-mini | $1/1M | $4/1M | $20/1M | $80/1M |

### 7.3 타임아웃 설정

장시간 작업에 대한 타임아웃 조정:

```bash
# 10분 타임아웃
python -m big_three_realtime_agents.main \
  --prompt "대규모 코드베이스를 분석해줘" \
  --timeout 600
```

### 7.4 Claude 모드 설정

`.env` 파일에서 Claude 동작 모드를 설정할 수 있습니다:

```env
# API 모드: Anthropic API 사용 (API 키 필요)
CLAUDE_MODE=api

# Max 모드: Claude Max 브라우저 사용 (API 키 불필요)
CLAUDE_MODE=max

# 자동: API 키가 있으면 API, 없으면 Max
CLAUDE_MODE=auto
```

### 7.5 고급 시스템 기능 토글

`.env` 파일에서 기능을 켜고 끌 수 있습니다:

```env
# Agent Pool 활성화 (154개 전문 에이전트)
ENABLE_AGENT_POOL=true

# 워크플로우 시스템
ENABLE_WORKFLOW=true

# 메모리 시스템 (세션 간 컨텍스트 유지)
ENABLE_MEMORY=true

# 학습 시스템 (성공/실패 패턴 학습)
ENABLE_LEARNING=true

# 보안 시스템 (감사 로깅)
ENABLE_SECURITY=true
```

### 7.6 대시보드 활용

Observability 대시보드로 시스템 모니터링:

```bash
# 대시보드만 실행
cd "/home/cafe99/MAS_proj/multiagent v4 - all/apps"
./START_HERE.sh
# 3번 선택
```

대시보드 URL: `http://localhost:5173`

제공 정보:
- 실시간 에이전트 상태
- 요청/응답 로그
- 성능 메트릭
- 에러 추적

---

## 8. 문제 해결

### 8.1 일반적인 오류

#### "OPENAI_API_KEY not found"
```bash
# .env 파일 확인
cat .env | grep OPENAI

# 해결: .env에 API 키 설정
echo "OPENAI_API_KEY=sk-proj-..." >> .env
```

#### "playwright not installed"
```bash
# Playwright 브라우저 설치
source .venv/bin/activate
playwright install chromium

# Linux에서 시스템 의존성 설치
playwright install-deps chromium
```

#### "ModuleNotFoundError"
```bash
# 가상환경 활성화 확인
source .venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

### 8.2 음성 모드 문제

#### 마이크가 인식되지 않음
```bash
# Linux: PulseAudio 확인
pulseaudio --check
pulseaudio --start

# 마이크 장치 확인
arecord -l
```

#### 음성 출력이 안 됨
```bash
# 스피커/헤드폰 확인
aplay -l

# 텍스트 출력으로 변경
python -m big_three_realtime_agents.main --input audio --output text
```

### 8.3 성능 문제

#### 응답이 느림
```bash
# mini 모델 사용
python -m big_three_realtime_agents.main --mini --prompt "..."

# Agent Pool 비활성화
# .env 수정
ENABLE_AGENT_POOL=false
```

#### 메모리 사용량이 높음
```bash
# 불필요한 기능 비활성화
ENABLE_LEARNING=false
ENABLE_MEMORY=false
```

### 8.4 로그 확인

```bash
# 실행 로그 확인
tail -f apps/realtime_poc/output_logs/*.log

# 감사 로그 확인
cat apps/content-gen/storage/security/audit.jsonl | jq .
```

---

## 9. 부록

### 9.1 디렉토리 구조

```
multiagent v4 - all/
├── apps/
│   ├── realtime_poc/              # 메인 애플리케이션
│   │   ├── big_three_realtime_agents/
│   │   │   ├── agents/            # 에이전트 구현
│   │   │   │   ├── openai/        # OpenAI Realtime
│   │   │   │   ├── claude/        # Claude Code
│   │   │   │   ├── gemini/        # Gemini Browser
│   │   │   │   └── pool/          # Agent Pool
│   │   │   ├── memory/            # 메모리 시스템
│   │   │   ├── learning/          # 학습 시스템
│   │   │   ├── security/          # 보안 시스템
│   │   │   ├── profiles/          # 프로파일 시스템
│   │   │   └── utils/             # 유틸리티
│   │   └── output_logs/           # 실행 로그
│   │
│   ├── content-gen/               # 작업 결과물 저장
│   │   ├── agents/                # 에이전트 레지스트리
│   │   └── storage/               # 영구 저장소
│   │
│   ├── observability-server/      # 모니터링 서버
│   └── observability-client/      # 대시보드 클라이언트
│
├── agentpool/                     # Agent Pool 정의
│   ├── core/                      # 핵심 에이전트 (15개)
│   ├── specialized/               # 전문 에이전트 (50+)
│   └── experimental/              # 실험 에이전트 (89+)
│
├── .env                           # 환경 설정
├── .env.sample                    # 환경 설정 템플릿
├── requirements.txt               # Python 의존성
├── setup.sh                       # 설치 스크립트
└── START_HERE.sh                  # 대화형 런처
```

### 9.2 환경 변수 전체 목록

| 변수 | 설명 | 필수 | 기본값 |
|-----|------|-----|-------|
| `OPENAI_API_KEY` | OpenAI API 키 | ✅ | - |
| `GEMINI_API_KEY` | Gemini API 키 | ✅ | - |
| `ANTHROPIC_API_KEY` | Anthropic API 키 | ❌ | - |
| `CLAUDE_MODE` | Claude 동작 모드 | ❌ | auto |
| `REALTIME_MODEL` | OpenAI 모델 | ❌ | gpt-realtime-2025-08-28 |
| `REALTIME_AGENT_VOICE` | 음성 선택 | ❌ | shimmer |
| `ENABLE_AGENT_POOL` | Agent Pool 활성화 | ❌ | true |
| `ENABLE_WORKFLOW` | 워크플로우 활성화 | ❌ | true |
| `ENABLE_MEMORY` | 메모리 시스템 | ❌ | true |
| `ENABLE_LEARNING` | 학습 시스템 | ❌ | true |
| `ENABLE_SECURITY` | 보안 시스템 | ❌ | true |
| `MAX_INSTANCES_PER_EXPERT` | 에이전트당 인스턴스 | ❌ | 3 |
| `AGENT_IDLE_TIMEOUT_MINUTES` | 유휴 타임아웃 | ❌ | 30 |

### 9.3 키보드 단축키

대화형 세션에서 사용 가능한 키:

| 키 | 동작 |
|---|------|
| `Ctrl+C` | 안전하게 종료 |
| `Ctrl+D` | 세션 종료 (EOF) |
| `Enter` | 텍스트 입력 전송 |

### 9.4 유용한 명령어 모음

```bash
# 프로파일 목록
python -m big_three_realtime_agents.main --list-profiles

# 워크플로우 목록
python -m big_three_realtime_agents.main --list-workflows

# 빠른 테스트
python -m big_three_realtime_agents.main --mini --prompt "Hello"

# 음성 테스트
python -m big_three_realtime_agents.main --voice --mini

# 로그 모니터링
tail -f apps/realtime_poc/output_logs/*.log

# 프로세스 정리
pkill -f "big_three\|observability"
```

### 9.5 자주 묻는 질문 (FAQ)

**Q: API 키 없이 사용할 수 있나요?**
A: OpenAI와 Gemini API 키는 필수입니다. Anthropic API 키 없이도 Claude Max 브라우저 모드로 사용 가능합니다.

**Q: 비용은 얼마나 드나요?**
A: 사용량에 따라 다릅니다. `--mini` 옵션으로 약 10배 절약 가능합니다.

**Q: 오프라인에서 사용 가능한가요?**
A: 아니요. 모든 AI 기능은 클라우드 API를 사용합니다.

**Q: 작업 결과물은 어디에 저장되나요?**
A: `apps/content-gen/` 디렉토리에 저장됩니다.

**Q: 이전 대화를 기억하나요?**
A: `ENABLE_MEMORY=true`로 설정하면 세션 간 컨텍스트가 유지됩니다.

---

## 연락처 및 지원

- **GitHub Issues**: https://github.com/cafe8601/-multi-agent-learning/issues
- **문서 업데이트**: 이 가이드의 최신 버전은 프로젝트 루트의 `USER_GUIDE.md`에서 확인하세요.

---

*이 가이드는 Big Three Realtime Agents v1.0을 기준으로 작성되었습니다.*
