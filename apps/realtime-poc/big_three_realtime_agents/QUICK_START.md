# Quick Start Guide

## For Developers Continuing the Refactoring

### Current Status
✅ **Foundation Complete** - All utilities, config, and base classes are ready
🔨 **Next Step** - Extract agent implementation code into modules

### File Guide

| Document | Purpose | When to Use |
|----------|---------|-------------|
| `README.md` | Architecture overview, design principles | Understanding the big picture |
| `REFACTORING_GUIDE.md` | Step-by-step implementation instructions | Actively implementing modules |
| `IMPLEMENTATION_STATUS.md` | Current status, checklists, metrics | Tracking progress |
| `QUICK_START.md` | This file - quick navigation | Finding what you need fast |

---

## Quick Reference

### Original File Location
```
/home/cafe99/voicetovoice/big-3-super-agent/apps/realtime-poc/big_three_realtime_agents.py
```
**Size:** 3,228 lines

### New Package Location
```
/home/cafe99/voicetovoice/big-3-super-agent/apps/realtime-poc/big_three_realtime_agents/
```

---

## Next Module to Create

### 1. agents/gemini/browser.py

**Extract from:** Lines 184-350 of original file
**Expected size:** ~150 lines
**Complexity:** Low-Medium

**Template:**
```python
"""Core GeminiBrowserAgent class."""

from pathlib import Path
from typing import Dict, Any, Optional
import uuid

from google import genai
from playwright.sync_api import sync_playwright

from ...config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TOOL,
    GEMINI_REGISTRY_PATH, AGENTS_BASE_DIR, GEMINI_TOOL_SLUG,
    AGENTIC_BROWSERING_TYPE, SCREEN_WIDTH, SCREEN_HEIGHT
)
from ...utils import AgentRegistry
from ..base import BaseAgent


class GeminiBrowserAgent(BaseAgent):
    """Browser automation agent powered by Gemini Computer Use API."""

    def __init__(self, logger=None):
        """Initialize browser agent."""
        super().__init__(logger, session_id=str(uuid.uuid4()))

        # Validate API key
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Initialize Gemini client
        self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)

        # Browser resources
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Initialize registry
        self.registry = AgentRegistry(
            registry_path=GEMINI_REGISTRY_PATH,
            base_dir=AGENTS_BASE_DIR,
            tool_slug=GEMINI_TOOL_SLUG,
            agent_type=AGENTIC_BROWSERING_TYPE,
            logger=self.logger
        )

    def setup(self):
        """Setup browser with Playwright."""
        # Copy from original lines 277-290
        pass

    def cleanup(self):
        """Cleanup browser resources."""
        # Copy from original lines 292-301
        pass

    def execute_task(self, task: str, agent_name: str,
                     url: Optional[str] = None, max_turns: int = 30) -> Dict[str, Any]:
        """Execute browser automation task."""
        # Copy from original lines 303-351
        pass
```

**To create:**
```bash
cd /home/cafe99/voicetovoice/big-3-super-agent/apps/realtime-poc
# Copy template above into new file
nano big_three_realtime_agents/agents/gemini/browser.py
# Fill in the implementations from original file
# Verify line count
wc -l big_three_realtime_agents/agents/gemini/browser.py
```

---

## Command Snippets

### View Original File Section
```bash
# View lines 184-350 (GeminiBrowserAgent start)
sed -n '184,350p' big_three_realtime_agents.py | less
```

### Check Module Line Counts
```bash
cd big_three_realtime_agents
find . -name "*.py" -exec sh -c 'echo "{}: $(wc -l < {})"' \;
```

### Test Module Import
```python
python3 -c "from big_three_realtime_agents.config import OPENAI_API_KEY; print('✅ Config imports work')"
python3 -c "from big_three_realtime_agents.utils import AudioManager; print('✅ Utils imports work')"
python3 -c "from big_three_realtime_agents.agents.base import BaseAgent; print('✅ Base imports work')"
```

### Validate New Module
```bash
# After creating a module
python3 -c "from big_three_realtime_agents.agents.gemini.browser import GeminiBrowserAgent; print('✅ Module works')"
```

---

## Implementation Pattern

For each new module:

1. **Read the original section**
   ```bash
   sed -n 'START,ENDp' big_three_realtime_agents.py
   ```

2. **Create the new file**
   ```bash
   nano big_three_realtime_agents/agents/AGENT/MODULE.py
   ```

3. **Add module structure**
   - Module docstring
   - Imports (config, utils, base)
   - Class/function definitions
   - Extract code from original

4. **Replace constants**
   - Direct constants → import from `config`
   - Utility functions → import from `utils`

5. **Test imports**
   ```python
   python3 -c "from big_three_realtime_agents.agents.AGENT.MODULE import CLASS"
   ```

6. **Verify line count**
   ```bash
   wc -l big_three_realtime_agents/agents/AGENT/MODULE.py
   ```
   Target: < 150 lines

7. **Update package __init__.py**
   ```python
   # In agents/AGENT/__init__.py
   from .MODULE import CLASS
   __all__ = ["CLASS"]
   ```

---

## Common Issues

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'big_three_realtime_agents'`

**Solution:** Ensure you're in the right directory:
```bash
cd /home/cafe99/voicetovoice/big-3-super-agent/apps/realtime-poc
python3 -m big_three_realtime_agents.MODULE
```

### Circular Imports
**Problem:** Modules import each other causing circular dependency

**Solutions:**
- Move shared code to `utils` or `config`
- Use late imports (import inside functions)
- Use type hints with strings

### Module Too Long
**Problem:** Module exceeds 150 lines

**Solutions:**
- Extract helper functions to separate module
- Move constants to `config`
- Simplify complex logic
- Create additional focused modules

---

## Cheat Sheet

### Import Patterns
```python
# Config
from ...config import OPENAI_API_KEY, RATE, FORMAT

# Utils
from ...utils import AudioManager, AgentRegistry, console, log_panel

# Base class
from ..base import BaseAgent

# Sibling module (same agent package)
from .functions import GeminiFunctionHandler
```

### Registry Usage
```python
# Old way (in original)
self.agent_registry = self._load_agent_registry()
self._save_agent_registry()

# New way (with AgentRegistry)
self.registry = AgentRegistry(
    registry_path=REGISTRY_PATH,
    base_dir=BASE_DIR,
    tool_slug=TOOL_SLUG,
    agent_type=AGENT_TYPE,
    logger=self.logger
)
self.registry.register_agent(name, metadata)
self.registry.get_agent(name)
```

---

## Testing Checklist

After creating each module:

- [ ] Module imports without errors
- [ ] Module is under 150 lines (or justified if over)
- [ ] Uses config imports for constants
- [ ] Uses utils imports for utilities
- [ ] Has comprehensive docstring
- [ ] Updated package __init__.py
- [ ] Tested basic functionality

---

## Progress Tracking

Mark modules as complete in `IMPLEMENTATION_STATUS.md`:
```markdown
- [x] agents/gemini/browser.py ✅
- [ ] agents/gemini/functions.py 🔨
```

---

## Getting Help

1. **Architecture Questions** → See `README.md`
2. **Implementation Details** → See `REFACTORING_GUIDE.md`
3. **Current Status** → See `IMPLEMENTATION_STATUS.md`
4. **Quick Reference** → This file

---

## Summary

**Foundation:** ✅ Complete (12 modules, 745 lines)
**Next:** 🔨 Extract GeminiBrowserAgent (3 modules, ~433 lines)
**Then:** 🔨 Extract ClaudeCodeAgenticCoder (6 modules, ~924 lines)
**Finally:** 🔨 Extract OpenAIRealtimeVoiceAgent (11 modules, ~1546 lines)

**Total Remaining:** ~20 modules, ~2,500 lines

**You've got this!** The hard architectural work is done. Now it's systematic extraction following the patterns established in the foundation modules.
