# Multi-Agent Learning System 가이드북

**버전**: 1.0
**대상 시스템**: Big Three Realtime Agents + Agent Pool
**목적**: 사용자 요청을 받아 자율적으로 작업을 완료하는 멀티에이전트 시스템

---

## 1. 시스템 개요

### 1.1 시스템 정체성

이 시스템은 **사용자 요청(텍스트/음성/문서 포함)을 받아 끝까지 자율적으로 작업을 완료하는 멀티에이전트 시스템**입니다.

```
[사용자 요청] → [오케스트레이터] → [전문 에이전트들] → [작업 완료]
       ↑                                                    ↓
       └──────────────── [결과 보고] ←─────────────────────┘
```

### 1.2 핵심 구성 요소

| 구성 요소 | 역할 | 기술 |
|-----------|------|------|
| **OpenAI Realtime Voice Agent** | 오케스트레이터 (지휘자) | OpenAI Realtime API, WebSocket |
| **Claude Agentic Coder** | 코드 작성/수정 | Claude API (또는 Claude Max) |
| **Gemini Browser Agent** | 웹 브라우저 자동화 | Gemini API, Playwright |
| **Agent Pool** | 154개 전문가 에이전트 | Markdown 정의, 동적 로딩 |

---

## 2. 작동 원리

### 2.1 전체 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                        사용자 요청                               │
│         "논문 초안 작성해줘" / "웹사이트 만들어줘"                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              OpenAI Realtime Voice Agent (오케스트레이터)         │
│                                                                  │
│  1. 요청 분석 (자연어 이해)                                       │
│  2. 작업 분해 (복잡한 작업 → 하위 작업들)                          │
│  3. 적절한 에이전트 선택 및 라우팅                                 │
│  4. 에이전트 간 조율 및 결과 통합                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Claude         │  │  Gemini Browser │  │   Agent Pool    │
│  Agentic Coder  │  │     Agent       │  │  (154 전문가)    │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • 코드 생성     │  │ • 웹 탐색       │  │ • Python Pro    │
│ • 파일 수정     │  │ • 정보 수집     │  │ • QA Expert     │
│ • 프로젝트 구축 │  │ • 폼 제출       │  │ • DevOps Eng    │
│ • 버그 수정     │  │ • 스크린샷      │  │ • Security...   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
              │               │               │
              └───────────────┴───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        작업 완료 및 결과 반환                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 각 에이전트 상세

#### 2.2.1 OpenAI Realtime Voice Agent (오케스트레이터)

**파일 위치**: `agents/openai/realtime.py`

**역할**: 전체 시스템의 지휘자. 사용자 요청을 받아 분석하고, 적절한 에이전트에게 작업을 분배

**핵심 기능**:
- 음성/텍스트 입력 처리
- 작업 의도 파악 및 분해
- 하위 에이전트 호출 (function calling)
- 결과 통합 및 사용자에게 반환

**사용 가능한 도구들**:
```python
# agents/openai/tools_agents.py - 에이전트 관리 도구
create_coding_agent()      # Claude 코딩 에이전트 생성
command_coding_agent()     # 코딩 작업 지시
check_coding_agent_result()# 결과 확인
execute_browser_task()     # 브라우저 작업 실행

# agents/openai/tools_filesystem.py - 파일 시스템 도구
read_local_file()          # 파일 읽기
write_local_file()         # 파일 쓰기
list_directory()           # 디렉토리 목록

# agents/openai/tools_browser.py - 브라우저 도구
execute_browser_task()     # 웹 작업 실행
```

#### 2.2.2 Claude Agentic Coder

**파일 위치**: `agents/claude/coder.py`

**역할**: 소프트웨어 개발 전문가. 코드 생성, 수정, 리팩토링 담당

**핵심 메서드**:
```python
create_agent(tool, agent_name)     # 새 에이전트 생성
command_agent(agent_name, prompt)  # 작업 지시
check_agent_result(agent_name)     # 결과 확인
list_agents()                      # 에이전트 목록
delete_agent(agent_name)           # 에이전트 삭제
```

**세션 관리**: 각 에이전트는 독립적인 세션을 유지하여 컨텍스트를 기억

#### 2.2.3 Gemini Browser Agent

**파일 위치**: `agents/gemini/browser.py`

**역할**: 웹 브라우저 자동화. 웹 검색, 정보 수집, 폼 제출 등

**핵심 메서드**:
```python
setup()                            # 브라우저 초기화
execute_task(task, url, max_turns) # 브라우저 작업 실행
cleanup()                          # 브라우저 종료
```

**작동 방식**:
1. Playwright로 브라우저 제어
2. 스크린샷 캡처 → Gemini Vision으로 분석
3. 다음 행동 결정 → 실행 → 반복 (최대 30턴)

---

## 3. 실행 방법

### 3.1 환경 설정

```bash
# 필수 환경 변수 (.env 파일)
OPENAI_API_KEY=your_openai_key      # OpenAI Realtime API
ANTHROPIC_API_KEY=your_anthropic_key # Claude API
GEMINI_API_KEY=your_gemini_key      # Gemini API
```

### 3.2 실행 명령어

```bash
# 텍스트 모드 (기본)
python -m big_three_realtime_agents.main

# 음성 모드
python -m big_three_realtime_agents.main --voice

# 자동 프롬프트 모드 (비대화형)
python -m big_three_realtime_agents.main --prompt "웹 앱을 만들어줘"

# 옵션
--input text|audio    # 입력 모드
--output text|audio   # 출력 모드
--mini               # 경량 모델 사용
--timeout 300        # 타임아웃 (초)
```

### 3.3 사용 예시

```
사용자: "Python으로 할 일 관리 앱을 만들어줘"

시스템 동작:
1. [오케스트레이터] 요청 분석 → 코딩 작업으로 판단
2. [오케스트레이터] Claude 코딩 에이전트 생성
3. [Claude Agent] 프로젝트 구조 설계
4. [Claude Agent] 코드 파일 생성 (main.py, models.py, ...)
5. [Claude Agent] 테스트 코드 작성
6. [오케스트레이터] 결과 통합 및 보고

결과: apps/content-gen/ 디렉토리에 완성된 앱
```

---

## 4. 시스템 아키텍처

### 4.1 디렉토리 구조

```
apps/realtime_poc/big_three_realtime_agents/
├── main.py                    # 진입점
├── config.py                  # 설정
├── logging_setup.py           # 로깅
│
├── agents/                    # 에이전트 모듈
│   ├── base.py               # 기본 에이전트 클래스
│   │
│   ├── openai/               # 오케스트레이터
│   │   ├── realtime.py       # 메인 클래스
│   │   ├── websocket_handlers.py
│   │   ├── function_handling.py
│   │   ├── tools_agents.py   # 에이전트 도구
│   │   ├── tools_browser.py  # 브라우저 도구
│   │   ├── tools_filesystem.py
│   │   └── ...
│   │
│   ├── claude/               # 코딩 에이전트
│   │   ├── coder.py          # 메인 클래스
│   │   ├── agent_creation.py
│   │   ├── agent_execution.py
│   │   ├── agent_lifecycle.py
│   │   └── ...
│   │
│   ├── gemini/               # 브라우저 에이전트
│   │   ├── browser.py        # 메인 클래스
│   │   ├── automation.py
│   │   ├── browser_actions.py
│   │   └── ...
│   │
│   └── pool/                 # 에이전트 풀
│       ├── agent_pool.py
│       ├── agent_selector.py
│       └── ...
│
├── memory/                    # 메모리 시스템
│   ├── memory_manager.py
│   ├── rag_system.py
│   └── ...
│
├── learning/                  # 학습 시스템
│   ├── learning_manager.py
│   ├── outcome_tracker.py
│   └── ...
│
├── workflow/                  # 워크플로우
│   ├── execution_engine.py
│   ├── workflow_planner.py
│   └── ...
│
├── security/                  # 보안
│   ├── security_manager.py
│   └── access_control.py
│
└── utils/                     # 유틸리티
    ├── ui.py
    ├── circuit_breaker.py
    └── retry.py
```

### 4.2 에이전트 간 통신

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenAI Realtime API                       │
│                      (WebSocket 연결)                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenAI Realtime Voice Agent                     │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Function    │    │ Message     │    │ Session     │     │
│  │ Handler     │    │ Processor   │    │ Manager     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Tool Execution Layer                    │   │
│  │  • AgentTools (Claude/Gemini 호출)                  │   │
│  │  • BrowserTools (브라우저 작업)                      │   │
│  │  • FilesystemTools (파일 I/O)                       │   │
│  │  • ReportingTools (결과 보고)                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │   Claude   │  │   Gemini   │  │   Agent    │
    │   Agent    │  │   Agent    │  │   Pool     │
    └────────────┘  └────────────┘  └────────────┘
```

---

## 5. Agent Pool 시스템

### 5.1 티어 구조

```
Agent Pool (154개 에이전트)
│
├── Tier 1: Core (20개) - 프로덕션 검증 완료
│   ├── backend-developer
│   ├── frontend-developer
│   ├── python-pro
│   ├── devops-engineer
│   ├── qa-expert
│   ├── security-auditor
│   └── ... (14개 더)
│
├── Tier 2: Specialized (~120개) - 전문 분야
│   ├── Languages: rust, go, java, kotlin...
│   ├── Frameworks: nextjs, django, rails...
│   ├── Infrastructure: terraform, k8s, sre...
│   ├── Quality: testing, performance...
│   ├── Security: penetration, compliance...
│   ├── Data/AI: mlops, data-science...
│   └── ... (5개 카테고리 더)
│
└── Tier 3: Experimental (~14개) - 실험적
    ├── Blockchain/Fintech
    ├── Gaming
    ├── Emerging Tech
    └── Niche
```

### 5.2 에이전트 선택 로직

```python
# agents/pool/agent_selector.py
def select_agent(task_description: str) -> Agent:
    """
    작업 설명을 분석하여 최적의 에이전트 선택

    1. 키워드 매칭: 작업에 포함된 기술 키워드 추출
    2. 카테고리 매칭: 키워드 → 관련 카테고리 매핑
    3. 티어 우선순위: Tier 1 > Tier 2 > Tier 3
    4. 전문성 점수: 에이전트별 전문성 점수 계산
    5. 최종 선택: 가장 높은 점수의 에이전트 반환
    """
```

---

## 6. 메모리 및 학습 시스템

### 6.1 메모리 시스템

**파일 위치**: `memory/`

```python
# 3-Tier 메모리 구조
Ephemeral   # 현재 작업 컨텍스트 (휘발성)
Short-Term  # 세션 내 기억 (세션 종료 시 삭제)
Long-Term   # 영구 저장 (패턴, 학습 결과)
```

### 6.2 RAG 시스템

**파일 위치**: `memory/rag_system.py`

- 코드베이스 인덱싱
- 시맨틱 검색
- 컨텍스트 증강

### 6.3 학습 시스템

**파일 위치**: `learning/`

```python
# learning/outcome_tracker.py
- 작업 결과 추적
- 성공/실패 패턴 분석
- 에이전트 성능 메트릭

# learning/pattern_analyzer.py
- 반복 패턴 감지
- 최적화 제안 생성
```

---

## 7. 논문 작성 시스템으로 활용

### 7.1 현재 시스템의 논문 작성 지원

이 시스템은 범용 자율 에이전트 시스템이므로, 논문 작성에도 활용 가능합니다:

```
사용자: "인공지능 윤리에 관한 논문 초안을 작성해줘"

시스템 동작:
1. [오케스트레이터] 요청 분석 → 문서 작성 + 리서치 작업
2. [Gemini Browser] 관련 논문/자료 웹 검색
3. [Claude Agent] 수집된 자료 기반 논문 구조 설계
4. [Claude Agent] 각 섹션별 초안 작성
5. [오케스트레이터] 결과 통합

결과: 논문 초안 파일 생성
```

### 7.2 논문 작성 특화를 위한 확장 방안

현재 시스템을 논문 작성에 최적화하려면:

1. **프롬프트 커스터마이징**: `agents/openai/system_prompt.py` 수정
2. **학술 검색 도구 추가**: `tools_browser.py`에 학술 DB 검색 기능
3. **인용 관리**: 새로운 도구 모듈 추가
4. **Agent Pool 활용**: `research-analyst`, `technical-writer` 에이전트

---

## 8. 문제 해결

### 8.1 일반적인 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `OPENAI_API_KEY not set` | 환경 변수 누락 | `.env` 파일 확인 |
| `playwright not found` | 의존성 미설치 | `pip install playwright && playwright install` |
| `WebSocket connection failed` | 네트워크 문제 | 인터넷 연결 확인 |
| `Agent timeout` | 작업 시간 초과 | `--timeout` 값 증가 |

### 8.2 로그 확인

```bash
# 로그 파일 위치
apps/realtime_poc/logs/

# 실시간 로그 확인
tail -f apps/realtime_poc/logs/agent.log
```

---

## 9. 핵심 코드 참조

### 9.1 오케스트레이터 초기화

```python
# agents/openai/realtime.py:52-108
class OpenAIRealtimeVoiceAgent(BaseAgent):
    def __init__(self, input_mode, output_mode, ...):
        # 하위 에이전트 초기화
        self.browser_agent = GeminiBrowserAgent(logger=self.logger)
        self.agentic_coder = ClaudeAgenticCoder(
            logger=self.logger,
            browser_agent=self.browser_agent
        )

        # 도구 모듈 초기화
        self.agent_tools = AgentTools(...)
        self.browser_tools = BrowserTools(...)
        self.filesystem_tools = FilesystemTools(...)
```

### 9.2 작업 실행 흐름

```python
# agents/openai/function_handling.py
class FunctionHandler:
    def handle_function_call(self, name, args):
        if name == "create_coding_agent":
            return self.agent_tools.create_agent(...)
        elif name == "command_coding_agent":
            return self.agent_tools.command_agent(...)
        elif name == "execute_browser_task":
            return self.browser_tools.execute_task(...)
```

---

## 10. 요약

| 항목 | 내용 |
|------|------|
| **시스템 유형** | 자율 멀티에이전트 오케스트레이션 |
| **오케스트레이터** | OpenAI Realtime Voice Agent |
| **실행 에이전트** | Claude Agentic Coder + Gemini Browser + Agent Pool |
| **입력 방식** | 음성 / 텍스트 / 자동 프롬프트 |
| **출력** | 완성된 작업물 (코드, 문서, 브라우저 작업 결과) |
| **확장성** | Agent Pool (154개 전문가) + 커스텀 에이전트 추가 가능 |

**핵심 개념**: 사용자는 자연어로 요청만 하면, 시스템이 자율적으로 작업을 분배하고 완료합니다.
