# 🔧 Exception Handling Guide - Production Best Practices

**Purpose**: Guide for improving exception handling from broad to specific
**Based On**: Session 2 analysis - 73 broad exception catches identified
**Target**: Professional error handling for production deployment

---

## 📊 Current Status

**Broad Exceptions Found**: 73 instances
**Distribution**:
- agents/: 50 (68%)
- memory/: 10 (14%)
- utils/: 6 (8%)
- security/: 2 (3%)
- learning/: 2 (3%)
- others: 3 (4%)

**Custom Exceptions Available**: 36 types (from exceptions.py)

---

## 🎯 Refactoring Patterns

### Pattern 1: Browser/Playwright Operations

**Before**:
```python
try:
    self.browser.launch()
    self.page.goto(url)
except Exception as exc:
    logger.error(f"Failed: {exc}")
    return {"ok": False}
```

**After**:
```python
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from ...exceptions import BrowserLaunchError, BrowserNavigationError

try:
    self.browser.launch()
    self.page.goto(url)
except PlaywrightTimeoutError as exc:
    logger.error(f"Browser operation timed out: {exc}")
    return {"ok": False, "error": "timeout"}
except BrowserLaunchError as exc:
    logger.error(f"Failed to launch browser: {exc}", exc_info=True)
    raise  # Re-raise for higher level handling
except BrowserNavigationError as exc:
    logger.warning(f"Navigation failed: {exc}")
    # Retry logic here if appropriate
    return {"ok": False, "error": str(exc)}
```

---

### Pattern 2: API Calls (OpenAI/Claude/Gemini)

**Before**:
```python
try:
    response = await client.messages.create(...)
except Exception as exc:
    logger.error(f"API call failed: {exc}")
```

**After**:
```python
from ...exceptions import OpenAIError, ClaudeError, GeminiError

try:
    response = await client.messages.create(...)
except anthropic.APIError as exc:
    logger.error(f"Claude API error: {exc}", exc_info=True)
    raise ClaudeError(f"API call failed: {exc}") from exc
except anthropic.RateLimitError as exc:
    logger.warning(f"Rate limited: {exc}")
    # Implement exponential backoff
    await asyncio.sleep(60)
    raise ClaudeError("Rate limit exceeded") from exc
```

---

### Pattern 3: File Operations

**Before**:
```python
try:
    with open(path) as f:
        data = json.load(f)
except Exception as exc:
    logger.error(f"Failed: {exc}")
```

**After**:
```python
from ...exceptions import MemoryRetrieveError, MemoryCorruptionError

try:
    with open(path) as f:
        data = json.load(f)
except FileNotFoundError as exc:
    logger.warning(f"File not found: {path}")
    raise MemoryRetrieveError(f"Data file missing: {path}") from exc
except json.JSONDecodeError as exc:
    logger.error(f"Corrupt data file: {path}", exc_info=True)
    raise MemoryCorruptionError(f"Invalid JSON in {path}") from exc
except PermissionError as exc:
    logger.error(f"Permission denied: {path}")
    raise MemoryRetrieveError(f"Cannot access {path}") from exc
```

---

### Pattern 4: Agent Operations

**Before**:
```python
try:
    agent = create_agent(name)
    result = agent.execute(task)
except Exception as exc:
    logger.error(f"Failed: {exc}")
```

**After**:
```python
from ...exceptions import (
    AgentCreationError,
    AgentExecutionError,
    AgentTimeoutError,
    AgentNotFoundError
)

try:
    agent = create_agent(name)
    result = agent.execute(task)
except AgentNotFoundError as exc:
    logger.warning(f"Agent not found: {name}")
    # Fallback to general agent
    agent = create_general_agent()
    result = agent.execute(task)
except AgentTimeoutError as exc:
    logger.error(f"Agent timed out: {exc}")
    # Retry with longer timeout
    result = agent.execute(task, timeout=300)
except AgentExecutionError as exc:
    logger.error(f"Execution failed: {exc}", exc_info=True)
    # Notify user of failure
    raise
```

---

### Pattern 5: Memory/Database Operations

**Before**:
```python
try:
    memory.store(key, value)
except Exception as exc:
    logger.error(f"Store failed: {exc}")
```

**After**:
```python
from ...exceptions import MemoryStoreError, MemoryCorruptionError

try:
    memory.store(key, value)
except (IOError, OSError) as exc:
    logger.error(f"Storage I/O error: {exc}", exc_info=True)
    raise MemoryStoreError(f"Cannot write to storage: {exc}") from exc
except ValueError as exc:
    logger.error(f"Invalid data format: {exc}")
    raise MemoryCorruptionError(f"Data validation failed: {exc}") from exc
```

---

## 🔄 Retry Logic Pattern

### Adding Resilience

**Install**:
```bash
pip install tenacity
```

**Pattern**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ClaudeError, OpenAIError))
)
async def call_llm_with_retry(prompt: str) -> str:
    """Call LLM with automatic retry on transient failures."""
    response = await client.messages.create(...)
    return response.content[0].text
```

---

## 📋 Priority Matrix for Refactoring

### 🔴 CRITICAL (Do First)

**Files**: 10 files
- `agents/claude/claude_max_adapter.py` (6 catches) ✅ Started
- `agents/openai/input_loops.py` (5 catches)
- `memory/rag_system.py` (5 catches)
- `utils/audio.py` (4 catches)
- `agents/openai/tools_pool.py` (4 catches)

**Impact**: Core functionality, highest usage

---

### 🟡 HIGH (Do Second)

**Files**: 15 files
- All other agents/ files
- memory/ files
- workflow/execution_engine.py

**Impact**: Important features

---

### 🟢 MEDIUM (Do Third)

**Files**: Remaining
- utils/, security/, learning/
- Less critical paths

---

## 🎯 Refactoring Strategy

### Approach 1: Complete (Ideal)

**Effort**: 6-8 hours
**Outcome**: All 73 exceptions refactored
**Grade Impact**: 91 → 94

---

### Approach 2: Critical Path (Practical)

**Effort**: 2-3 hours
**Outcome**: Top 20 critical exceptions refactored
**Grade Impact**: 91 → 92
**Remaining**: 53 exceptions documented for gradual improvement

---

### Approach 3: Documented Pattern (Pragmatic)

**Effort**: 1 hour
**Outcome**: Patterns documented, team can refactor incrementally
**Grade Impact**: 91 (no immediate change)
**Future**: Improve during maintenance

---

## 📝 Implementation Checklist

### For Each Broad Exception:

- [ ] Identify the operation (file I/O, API call, browser, etc.)
- [ ] Determine possible failure modes
- [ ] Select appropriate specific exception(s)
- [ ] Import custom exception at top of file
- [ ] Replace broad catch with specific catches
- [ ] Add appropriate logging (with exc_info=True)
- [ ] Consider retry logic if transient failure
- [ ] Decide: re-raise, handle, or return error

---

## 🔍 Quick Reference

### Exception Mapping

| Operation | Use Exception |
|-----------|--------------|
| Browser launch | `BrowserLaunchError` |
| Browser navigation | `BrowserNavigationError` |
| Browser actions | `BrowserActionError` |
| Claude API | `ClaudeError` |
| OpenAI API | `OpenAIError` |
| Gemini API | `GeminiError` |
| File I/O | `MemoryStoreError`, `MemoryRetrieveError` |
| JSON parsing | `MemoryCorruptionError` |
| Agent creation | `AgentCreationError` |
| Agent execution | `AgentExecutionError` |
| Workflow | `WorkflowExecutionError` |
| Config | `ConfigurationError` |
| Auth | `AuthorizationError` |

---

## ✅ Validation

### After Refactoring

**Check**:
```bash
# 1. Syntax validation
python3 -m py_compile apps/realtime-poc/big_three_realtime_agents/**/*.py

# 2. Import validation
python3 -c "from apps.realtime_poc.big_three_realtime_agents import exceptions"

# 3. Test that exceptions work
pytest tests/ -v
```

---

## 🎓 Best Practices

1. **Specific > Generic**: Always prefer specific exceptions
2. **Context**: Add context to error messages
3. **Logging**: Use `exc_info=True` for stack traces
4. **Chaining**: Use `from exc` to preserve original error
5. **Recovery**: Implement retry for transient failures
6. **Documentation**: Document expected exceptions in docstrings

---

**Guide Version**: 1.0
**Created**: 2025-11-09 (Session 2)
**Status**: Ready for team use
