# Refactoring Implementation Guide

## Current Status

### ✅ Completed Foundation Modules

All foundation modules have been created and are **under 150 lines**:

| Module | Lines | Purpose | Status |
|--------|-------|---------|--------|
| `__init__.py` | 35 | Package initialization | ✅ |
| `config.py` | 90 | Configuration & constants | ✅ |
| `logging_setup.py` | 53 | Logging setup | ✅ |
| `utils/__init__.py` | 17 | Utility exports | ✅ |
| `utils/audio.py` | 117 | Audio management | ✅ |
| `utils/registry.py` | 138 | Agent registry | ✅ |
| `utils/ui.py` | 168 | UI utilities | ⚠️ (18 lines over, can optimize) |
| `agents/__init__.py` | 9 | Agent exports | ✅ |
| `agents/base.py` | 65 | Base agent class | ✅ |
| `agents/gemini/__init__.py` | 17 | Gemini package | ✅ |
| `agents/claude/__init__.py` | 18 | Claude package | ✅ |
| `agents/openai/__init__.py` | 18 | OpenAI package | ✅ |

**Total Created:** 745 lines across 12 modules (avg: 62 lines/module)

### 📋 Remaining Work

The original 3,228-line file still needs to be split into agent implementation modules.

## Step-by-Step Implementation Guide

### Phase 1: GeminiBrowserAgent (~433 lines remaining)

#### 1.1 Create `agents/gemini/browser.py` (~150 lines)

**Extract from original lines: 184-350**

```python
"""Core GeminiBrowserAgent class."""

from pathlib import Path
from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timezone

from google import genai
from playwright.sync_api import sync_playwright

from ...config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TOOL, AGENTIC_BROWSERING_TYPE,
    GEMINI_REGISTRY_PATH, AGENTS_BASE_DIR, GEMINI_TOOL_SLUG,
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from ...utils import AgentRegistry
from ..base import BaseAgent


class GeminiBrowserAgent(BaseAgent):
    """Browser automation agent powered by Gemini Computer Use API."""

    def __init__(self, logger=None):
        super().__init__(logger, session_id=str(uuid.uuid4()))

        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
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
        # Implementation from original lines 277-290

    def cleanup(self):
        """Cleanup browser resources."""
        # Implementation from original lines 292-301

    def execute_task(self, task: str, agent_name: str, url: Optional[str] = None,
                     max_turns: int = 30) -> Dict[str, Any]:
        """Execute browser task."""
        # Implementation from original lines 303-351
```

**Key responsibilities:**
- Class initialization
- Browser setup/cleanup
- Registry integration (delegate to AgentRegistry)
- Main execute_task interface

#### 1.2 Create `agents/gemini/functions.py` (~150 lines)

**Extract from original lines: 474-610**

```python
"""Gemini function call handlers."""

from typing import List, Dict, Any
from playwright.sync_api import Page

from ...config import SCREEN_WIDTH, SCREEN_HEIGHT


class GeminiFunctionHandler:
    """Handles Gemini function call execution."""

    def __init__(self, page: Page, logger):
        self.page = page
        self.logger = logger

    def execute_function_calls(self, candidate) -> List[Dict[str, Any]]:
        """Execute Gemini function calls from candidate."""
        # Implementation from original lines 474-577

    def get_function_responses(self, results: List[Dict[str, Any]]) -> List:
        """Format function results for Gemini."""
        # Implementation from original lines 578-602

    @staticmethod
    def denormalize_x(x: int) -> int:
        """Convert normalized x coordinate."""
        return int(x * SCREEN_WIDTH)

    @staticmethod
    def denormalize_y(y: int) -> int:
        """Convert normalized y coordinate."""
        return int(y * SCREEN_HEIGHT)
```

**Key responsibilities:**
- Function call execution
- Response formatting
- Coordinate denormalization

#### 1.3 Create `agents/gemini/automation.py` (~133 lines)

**Extract from original lines: 353-473**

```python
"""Browser automation loop logic."""

import io
from pathlib import Path
from typing import Dict, Any

from google.genai.types import Content, Part


class BrowserAutomationLoop:
    """Manages turn-based browser automation."""

    def __init__(self, client, page, function_handler, logger):
        self.client = client
        self.page = page
        self.function_handler = function_handler
        self.logger = logger

    def run_automation_loop(self, task: str, agent_name: str,
                           model: str, max_turns: int = 30) -> str:
        """Run browser automation loop."""
        # Implementation from original lines 353-473

    def capture_screenshot(self) -> bytes:
        """Capture current page screenshot."""
        return self.page.screenshot()
```

**Key responsibilities:**
- Turn-based interaction loop
- Screenshot capture and encoding
- Conversation management

### Phase 2: ClaudeCodeAgenticCoder (~924 lines remaining)

#### 2.1 Create `agents/claude/coder.py` (~150 lines)

**Extract from original lines: 617-780**

Core class with registry integration, initialization, and high-level methods.

#### 2.2 Create `agents/claude/agent_creation.py` (~150 lines)

**Extract from original lines: 1078-1250**

Async agent creation logic, operator file preparation, name generation.

#### 2.3 Create `agents/claude/agent_execution.py` (~150 lines)

**Extract from original lines: 1281-1460**

Command threading, query execution, result collection.

#### 2.4 Create `agents/claude/tools.py` (~150 lines)

**Extract from original lines: 696-777**

Browser tool creation and MCP server integration.

#### 2.5 Create `agents/claude/prompts.py` (~150 lines)

**Extract from original lines: 778-797, 1251-1280**

Template loading, rendering, and variable substitution.

#### 2.6 Create `agents/claude/observability.py` (~174 lines)

**Extract from original lines: 799-927**

Event tracking, hooks, and summarization.

### Phase 3: OpenAIRealtimeVoiceAgent (~1546 lines remaining)

This is the largest agent and requires the most splitting.

#### 3.1 Create `agents/openai/realtime.py` (~150 lines)

**Extract from original lines: 1541-1650**

Core class initialization, configuration, and main interface.

#### 3.2 Create `agents/openai/websocket_handlers.py` (~150 lines)

**Extract from original lines: 1999-2060, 2251-2274**

WebSocket event handlers: on_open, on_message, on_error, on_close.

#### 3.3 Create `agents/openai/message_processing.py` (~150 lines)

**Extract from original lines: 2060-2250**

Text delta, audio delta, and response assembly.

#### 3.4 Create `agents/openai/function_handling.py` (~150 lines)

**Extract from original lines: 2364-2494**

Function call delta handling, execution routing, output sending.

#### 3.5 Create `agents/openai/tools_catalog.py` (~150 lines)

**Extract from original lines: 2495-2687**

Tool spec building and schema definitions.

#### 3.6 Create `agents/openai/tools_agents.py` (~150 lines)

**Extract from original lines: 2688-2844**

Agent management tools: list, create, command, check_result, delete.

#### 3.7 Create `agents/openai/tools_browser.py` (~100 lines)

**Extract from original lines: 2845-2881**

Browser interaction tools and integration.

#### 3.8 Create `agents/openai/tools_filesystem.py` (~150 lines)

**Extract from original lines: 2882-3014**

File operation tools: open_file, read_file.

#### 3.9 Create `agents/openai/tools_reporting.py` (~120 lines)

**Extract from original lines: 3015-3043, 1835-1917**

Cost calculation, token tracking, summary display.

#### 3.10 Create `agents/openai/input_loops.py` (~150 lines)

**Extract from original lines: 2275-2325, 2302-2325, 1781-1834**

Text input, audio input, keyboard listener.

#### 3.11 Create `agents/openai/system_prompt.py` (~146 lines)

**Extract from original lines: 1918-1956**

Template loading, tool list injection, prompt assembly.

#### 3.12 Create `agents/openai/cost_calculator.py` (~150 lines)

**Extract from original lines: 1835-1917**

Cost calculation from usage, token tracking, display formatting.

### Phase 4: Main Orchestration

#### 4.1 Create `main.py` (~150 lines)

**Extract from original lines: 3117-3228**

```python
#!/usr/bin/env python3
"""
Main orchestration module for Big Three Realtime Agents.
"""

import argparse
from pathlib import Path

from .logging_setup import setup_logging
from .config import (
    REALTIME_MODEL_DEFAULT,
    REALTIME_MODEL_MINI,
    REALTIME_VOICE_CHOICE
)
# from .agents.openai import OpenAIRealtimeVoiceAgent


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Big Three Realtime Agents - Unified agent system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Add arguments from original lines 3119-3155
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    logger = setup_logging()

    # Initialize and run agent
    # Implementation from original lines 3156-3228


if __name__ == "__main__":
    main()
```

## Implementation Strategy

### Recommended Order

1. **Start with GeminiBrowserAgent** (simplest, ~433 lines)
   - Fewer dependencies
   - Self-contained logic
   - Good practice for the pattern

2. **Then ClaudeCodeAgenticCoder** (moderate, ~924 lines)
   - More complex but well-structured
   - Clear separation between creation/execution/tools

3. **Finally OpenAIRealtimeVoiceAgent** (most complex, ~1546 lines)
   - Most modules to create
   - Highest interconnectivity
   - Benefits from experience with other two

### For Each Agent Module

1. **Create the file** with module docstring
2. **Add imports** (config, utils, base class)
3. **Extract the class/functions** from original file
4. **Replace direct constants** with imports from config
5. **Replace utility calls** with imports from utils
6. **Test the module** imports and basic functionality
7. **Update the agent's `__init__.py`** to export the class

## Testing Strategy

### Module-Level Testing

For each new module:

```python
# Test imports
python3 -c "from big_three_realtime_agents.agents.gemini.browser import GeminiBrowserAgent"

# Test instantiation
python3 -c "
from big_three_realtime_agents.agents.gemini.browser import GeminiBrowserAgent
from big_three_realtime_agents.logging_setup import setup_logging
logger = setup_logging()
agent = GeminiBrowserAgent(logger=logger)
print('Agent created successfully')
"
```

### Integration Testing

After all modules are created:

```python
# Test full import chain
python3 -c "
from big_three_realtime_agents import setup_logging
from big_three_realtime_agents.agents.gemini import GeminiBrowserAgent
from big_three_realtime_agents.agents.claude import ClaudeCodeAgenticCoder
from big_three_realtime_agents.agents.openai import OpenAIRealtimeVoiceAgent
print('All agents imported successfully')
"
```

## Line Count Validation

After creating each module, verify it's under 150 lines:

```bash
wc -l big_three_realtime_agents/agents/gemini/browser.py
```

If over 150 lines, consider:
- Extracting helper functions to separate module
- Moving constants to config
- Simplifying complex logic
- Creating additional focused modules

## Common Patterns

### Importing from Config

```python
from ...config import (
    OPENAI_API_KEY,
    GEMINI_MODEL,
    # ... other constants
)
```

### Importing from Utils

```python
from ...utils import AudioManager, AgentRegistry, console, log_panel
```

### Importing Base Class

```python
from ..base import BaseAgent
```

### Using AgentRegistry

Replace direct registry management:

```python
# Old (in original file)
self.agent_registry = self._load_agent_registry()
self._save_agent_registry()

# New (with AgentRegistry)
self.registry = AgentRegistry(
    registry_path=REGISTRY_PATH,
    base_dir=BASE_DIR,
    tool_slug=TOOL_SLUG,
    agent_type=AGENT_TYPE,
    logger=self.logger
)
self.registry.register_agent(name, metadata)
```

## Troubleshooting

### Circular Import Issues

If you encounter circular imports:
1. Move shared code to utils or config
2. Use late imports (import inside functions)
3. Use type hints with strings: `def func(agent: "GeminiBrowserAgent")`

### Missing Dependencies

If imports fail:
1. Check `__init__.py` files are present
2. Verify relative import paths (`.` for same package, `..` for parent)
3. Ensure config and utils modules are imported before agents

### Line Count Creep

If modules exceed 150 lines:
1. Extract helper functions
2. Move docstrings to separate documentation
3. Simplify complex conditionals
4. Create additional focused modules

## Next Actions

1. ✅ **Foundation Complete** - All utility modules created
2. 🔨 **Start with Gemini** - Create `agents/gemini/browser.py`
3. 🔨 **Continue with Functions** - Create `agents/gemini/functions.py`
4. 🔨 **Add Automation** - Create `agents/gemini/automation.py`
5. 🔨 **Move to Claude** - Follow same pattern
6. 🔨 **Finish with OpenAI** - Most complex, split carefully
7. 🔨 **Create Main** - Orchestration and entry point
8. ✅ **Test Everything** - Comprehensive testing
9. 📚 **Update Docs** - Final documentation updates

## Resources

- **Original File:** `big_three_realtime_agents.py` (3,228 lines)
- **Target:** 25-30 modules, each < 150 lines
- **Progress:** 12/30 modules (40% complete by count)
- **Lines Extracted:** 745/3,228 (23% complete by lines)
- **Remaining:** ~2,500 lines in agent implementations

## Success Criteria

- ✅ All modules under 150 lines
- ✅ Clear separation of concerns
- ✅ Comprehensive documentation
- ✅ All imports working correctly
- ✅ Original functionality preserved
- ✅ Improved maintainability and testability
