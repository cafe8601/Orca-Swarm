# Big Three Realtime Agents - Modular Architecture

## Overview

This directory contains the refactored modular architecture of the Big Three Realtime Agents system, breaking down the original 3,228-line monolithic file into maintainable modules under 150 lines each.

## Architecture

```
big_three_realtime_agents/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration and constants (98 lines)
├── logging_setup.py            # Logging configuration (54 lines)
├── utils/                      # Utility modules
│   ├── __init__.py            # Utility exports (16 lines)
│   ├── audio.py               # Audio management (122 lines)
│   ├── registry.py            # Agent registry base class (139 lines)
│   └── ui.py                  # Rich console UI utilities (147 lines)
├── agents/                     # Agent implementations
│   ├── __init__.py            # Agent exports
│   ├── base.py                # Base agent class (66 lines)
│   ├── gemini/                # Gemini Computer Use agent
│   │   ├── __init__.py       # Module documentation
│   │   ├── browser.py         # GeminiBrowserAgent core (~400 lines to split)
│   │   └── functions.py       # Gemini function handlers (~200 lines to split)
│   ├── claude/                # Claude Code agent
│   │   ├── __init__.py       # Module documentation
│   │   ├── coder.py           # ClaudeCodeAgenticCoder core (~600 lines to split)
│   │   ├── tools.py           # Tool implementations (~300 lines to split)
│   │   └── prompts.py         # Prompt handling (~150 lines)
│   └── openai/                # OpenAI Realtime API agent
│       ├── __init__.py        # Module documentation
│       ├── realtime.py        # OpenAIRealtimeVoiceAgent core (~800 lines to split)
│       ├── tools.py           # Tool definitions (~400 lines to split)
│       └── websocket.py       # WebSocket handlers (~300 lines to split)
└── main.py                     # Main orchestration (to be created)
```

## Module Breakdown

### Configuration (`config.py`)
**Size:** 98 lines
**Purpose:** Centralized configuration management
- OpenAI Realtime API configuration
- Audio configuration constants
- Claude Code SDK configuration
- Gemini Computer Use configuration
- Directory paths and registry locations
- Model pricing information

### Logging (`logging_setup.py`)
**Size:** 54 lines
**Purpose:** Centralized logging setup
- File-based logging configuration
- Timestamp-based log file naming
- Logger initialization

### Utility Modules

#### Audio (`utils/audio.py`)
**Size:** 122 lines
**Purpose:** Audio management and utilities
- `AudioManager` class for PyAudio interface management
- Audio encoding/decoding (base64)
- Beep tone generation for UI feedback
- Audio stream setup and cleanup

#### Registry (`utils/registry.py`)
**Size:** 139 lines
**Purpose:** Agent registration and metadata management
- `AgentRegistry` base class for agent tracking
- JSON-based registry persistence
- Thread-safe registry operations
- Agent directory management

#### UI (`utils/ui.py`)
**Size:** 147 lines
**Purpose:** Rich console UI formatting
- Panel-based message display
- Tool catalog visualization
- Agent roster table display
- Tool request formatting

### Agent Base Class (`agents/base.py`)
**Size:** 66 lines
**Purpose:** Common agent interface
- Abstract base class defining agent contract
- Common logging methods
- Session ID management
- Setup/cleanup/execute_task interface

## Refactoring Strategy

### Original Structure
- **Single file:** `big_three_realtime_agents.py` (3,228 lines)
- Three large agent classes embedded in one file
- All utilities, configuration, and logic intermingled

### Target Structure
Each agent class will be split into focused modules:

#### GeminiBrowserAgent (~433 lines) → Split into 3-4 modules
1. **browser.py** (~150 lines): Core agent class and initialization
   - Registry management delegation
   - Browser setup/cleanup
   - Main execute_task method

2. **functions.py** (~150 lines): Function call handling
   - Gemini function call execution
   - Function response formatting
   - Coordinate normalization

3. **automation.py** (~133 lines): Browser automation loop
   - Turn-based interaction logic
   - Screenshot capture
   - Action execution

#### ClaudeCodeAgenticCoder (~924 lines) → Split into 6-7 modules
1. **coder.py** (~150 lines): Core agent class
   - Registry management
   - Agent lifecycle (create/command/delete)

2. **agent_creation.py** (~150 lines): Agent creation logic
   - Async agent creation
   - Operator file preparation
   - Name generation

3. **agent_execution.py** (~150 lines): Agent command execution
   - Command threading
   - Query execution
   - Result collection

4. **tools.py** (~150 lines): Browser tool creation
   - MCP server integration
   - Tool specification generation

5. **prompts.py** (~150 lines): Prompt management
   - Template loading
   - Prompt rendering
   - Variable substitution

6. **observability.py** (~174 lines): Event tracking
   - Event hook creation
   - Event summarization
   - Observability logging

#### OpenAIRealtimeVoiceAgent (~1546 lines) → Split into 10-12 modules
1. **realtime.py** (~150 lines): Core agent class
   - Initialization
   - Configuration
   - Main connection logic

2. **websocket_handlers.py** (~150 lines): WebSocket event handlers
   - on_open, on_message, on_error, on_close
   - Event routing

3. **message_processing.py** (~150 lines): Message handling
   - Text delta processing
   - Audio delta processing
   - Response assembly

4. **function_handling.py** (~150 lines): Function call processing
   - Function call delta handling
   - Function execution routing
   - Output sending

5. **tools_catalog.py** (~150 lines): Tool specifications
   - Tool spec building
   - Tool schema definitions

6. **tools_agents.py** (~150 lines): Agent management tools
   - list_agents, create_agent
   - command_agent, check_agent_result
   - delete_agent

7. **tools_browser.py** (~150 lines): Browser interaction tools
   - browser_use implementation
   - Browser agent integration

8. **tools_filesystem.py** (~150 lines): File operation tools
   - open_file, read_file
   - File content processing

9. **tools_reporting.py** (~150 lines): Cost and reporting tools
   - Cost calculation
   - Token usage tracking
   - Summary display

10. **input_loops.py** (~150 lines): Input handling
    - Text input loop
    - Audio input loop
    - Keyboard listener

11. **system_prompt.py** (~146 lines): System prompt management
    - Template loading
    - Dynamic tool list injection
    - Prompt assembly

## Benefits of Modular Architecture

### Maintainability
- **Single Responsibility:** Each module has a clear, focused purpose
- **Easier Navigation:** Find functionality quickly by module name
- **Reduced Complexity:** Smaller files are easier to understand
- **Better Organization:** Related functionality grouped logically

### Testability
- **Unit Testing:** Test individual modules in isolation
- **Mock Dependencies:** Easier to mock smaller interfaces
- **Focused Tests:** Test files mirror module structure

### Scalability
- **Independent Evolution:** Modules can be enhanced independently
- **Team Collaboration:** Multiple developers can work in parallel
- **Clear Boundaries:** Well-defined interfaces between modules

### Code Quality
- **Reduced Cognitive Load:** Understand one concept at a time
- **Better Encapsulation:** Internal details hidden within modules
- **Easier Refactoring:** Change implementation without affecting consumers
- **Clear Dependencies:** Import statements show module relationships

## Implementation Status

### Completed ✓
- [x] Directory structure created
- [x] Configuration module (config.py)
- [x] Logging module (logging_setup.py)
- [x] Audio utilities (utils/audio.py)
- [x] Registry utilities (utils/registry.py)
- [x] UI utilities (utils/ui.py)
- [x] Base agent class (agents/base.py)
- [x] Package __init__ files

### To Be Implemented
- [ ] GeminiBrowserAgent modules
  - [ ] browser.py
  - [ ] functions.py
  - [ ] automation.py

- [ ] ClaudeCodeAgenticCoder modules
  - [ ] coder.py
  - [ ] agent_creation.py
  - [ ] agent_execution.py
  - [ ] tools.py
  - [ ] prompts.py
  - [ ] observability.py

- [ ] OpenAIRealtimeVoiceAgent modules
  - [ ] realtime.py
  - [ ] websocket_handlers.py
  - [ ] message_processing.py
  - [ ] function_handling.py
  - [ ] tools_catalog.py
  - [ ] tools_agents.py
  - [ ] tools_browser.py
  - [ ] tools_filesystem.py
  - [ ] tools_reporting.py
  - [ ] input_loops.py
  - [ ] system_prompt.py

- [ ] Main orchestration module (main.py)
- [ ] Migration path documentation
- [ ] Testing framework setup

## Migration Path

### Phase 1: Foundation (Completed)
1. Create directory structure
2. Extract configuration and constants
3. Extract utility modules
4. Create base classes

### Phase 2: Agent Extraction (Current)
1. Extract GeminiBrowserAgent
   - Create browser.py with core class
   - Extract function handlers to functions.py
   - Extract automation loop to automation.py

2. Extract ClaudeCodeAgenticCoder
   - Create coder.py with core class
   - Extract agent creation logic
   - Extract agent execution logic
   - Extract tool creation
   - Extract prompt management
   - Extract observability

3. Extract OpenAIRealtimeVoiceAgent
   - Create realtime.py with core class
   - Extract WebSocket handlers
   - Extract message processing
   - Extract function handling
   - Split tool implementations
   - Extract input loops
   - Extract system prompt logic

### Phase 3: Integration
1. Create main orchestration module
2. Update entry point script
3. Ensure backward compatibility
4. Create import adapters if needed

### Phase 4: Validation
1. Test all modules independently
2. Integration testing
3. Performance validation
4. Documentation updates

## Usage

### Importing Utilities
```python
from big_three_realtime_agents.config import OPENAI_API_KEY, GEMINI_API_KEY
from big_three_realtime_agents.logging_setup import setup_logging
from big_three_realtime_agents.utils import AudioManager, AgentRegistry, console
```

### Importing Agents (Once Implemented)
```python
from big_three_realtime_agents.agents.gemini import GeminiBrowserAgent
from big_three_realtime_agents.agents.claude import ClaudeCodeAgenticCoder
from big_three_realtime_agents.agents.openai import OpenAIRealtimeVoiceAgent
```

### Running the System
```bash
# Using the refactored modules
python -m big_three_realtime_agents.main --input text --output text

# Or with the original script (backward compatible)
uv run big_three_realtime_agents.py --input text --output text
```

## Design Principles

### Module Size
- Target: **< 150 lines per module**
- Reasoning: Fits on a single screen, easy to comprehend
- Exception: Complex but cohesive logic may reach 150-200 lines

### Naming Conventions
- **Modules:** snake_case (e.g., `websocket_handlers.py`)
- **Classes:** PascalCase (e.g., `AudioManager`)
- **Functions:** snake_case (e.g., `setup_logging()`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `OPENAI_API_KEY`)

### Dependency Management
- **Configuration:** Imported from `config.py`
- **Utilities:** Imported from `utils` package
- **Agents:** Self-contained with minimal cross-dependencies
- **Circular Dependencies:** Avoided through careful interface design

### Error Handling
- Each module handles its own errors
- Errors propagate with context
- Logging at appropriate levels

## Next Steps

1. **Extract Agent Classes:** Systematically split large agent classes
2. **Create Tests:** Add unit tests for each module
3. **Documentation:** Add docstrings to all public interfaces
4. **Performance Testing:** Ensure refactoring doesn't impact performance
5. **Migration Guide:** Create step-by-step migration documentation

## Contributing

When adding new functionality:
1. Identify the appropriate module or create a new focused module
2. Keep modules under 150 lines
3. Add comprehensive docstrings
4. Update this README with changes
5. Add tests for new functionality

## References

- Original monolithic file: `big_three_realtime_agents.py` (3,228 lines)
- Refactoring target: ~25-30 focused modules averaging 100-130 lines each
