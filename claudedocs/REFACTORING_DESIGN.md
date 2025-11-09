# Big-3-Super-Agent Refactoring Design Specification

## Executive Summary
Complete system redesign from monolithic 3,228-line file to modular architecture with 150+ specialized agents and <150 line file constraint.

**Design Goals:**
- Modular architecture with clear separation of concerns
- All files <150 lines for maintainability
- Leverage 150+ specialized agents from agentpool
- Scalable agent orchestration system
- Clean interfaces and dependency management

---

## 1. Architecture Overview

### 1.1 System Layers

```
┌─────────────────────────────────────────────────────┐
│          Presentation Layer (CLI/Voice)             │
├─────────────────────────────────────────────────────┤
│         Orchestration Layer (Coordinator)           │
├─────────────────────────────────────────────────────┤
│      Agent Management Layer (Pool + Registry)       │
├─────────────────────────────────────────────────────┤
│     Tool System Layer (9 Core + Agent Tools)        │
├─────────────────────────────────────────────────────┤
│   Communication Layer (WebSocket + Streaming)       │
├─────────────────────────────────────────────────────┤
│      Infrastructure Layer (Storage + Config)        │
└─────────────────────────────────────────────────────┘
```

### 1.2 Core Principles
- **Single Responsibility**: Each module handles one concern
- **Dependency Injection**: Loose coupling via interfaces
- **Event-Driven**: Async communication via event bus
- **Plugin Architecture**: Agents as pluggable modules
- **Configuration-Based**: External config over hardcoding

---

## 2. Directory Structure Design

```
big-3-super-agent/
├── src/
│   ├── core/                          # Core orchestration (10 files)
│   │   ├── __init__.py
│   │   ├── orchestrator.py            # Main coordinator <150 lines
│   │   ├── session_manager.py         # Session lifecycle
│   │   ├── event_bus.py               # Event distribution
│   │   └── config_loader.py           # Configuration management
│   │
│   ├── agents/                        # Agent management (15 files)
│   │   ├── __init__.py
│   │   ├── base/                      # Base classes
│   │   │   ├── agent_interface.py     # Agent contract
│   │   │   ├── agent_registry.py      # Registration system
│   │   │   └── agent_lifecycle.py     # Creation/destruction
│   │   │
│   │   ├── claude/                    # Claude Code agents
│   │   │   ├── __init__.py
│   │   │   ├── claude_agent.py        # Claude wrapper
│   │   │   ├── claude_factory.py      # Agent creation
│   │   │   ├── claude_session.py      # Session management
│   │   │   └── claude_tools.py        # Tool integration
│   │   │
│   │   ├── gemini/                    # Gemini browser agents
│   │   │   ├── __init__.py
│   │   │   ├── gemini_agent.py        # Gemini wrapper
│   │   │   ├── gemini_browser.py      # Browser control
│   │   │   ├── gemini_automation.py   # Computer Use loop
│   │   │   └── gemini_screenshot.py   # Screenshot mgmt
│   │   │
│   │   └── pool/                      # Agent pool system
│   │       ├── __init__.py
│   │       ├── pool_manager.py        # Pool coordination
│   │       ├── pool_loader.py         # Agent loading
│   │       └── pool_selector.py       # Agent selection
│   │
│   ├── tools/                         # Tool system (20 files)
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── tool_interface.py      # Tool contract
│   │   │   ├── tool_registry.py       # Tool registration
│   │   │   └── tool_executor.py       # Execution engine
│   │   │
│   │   ├── core_tools/                # 9 core tools
│   │   │   ├── list_agents.py         # <150 lines each
│   │   │   ├── create_agent.py
│   │   │   ├── command_agent.py
│   │   │   ├── check_result.py
│   │   │   ├── delete_agent.py
│   │   │   ├── browser_use.py
│   │   │   ├── file_ops.py
│   │   │   └── report_costs.py
│   │   │
│   │   └── agent_tools/               # Agent-specific tools
│   │       └── browser_tool.py        # Claude browser access
│   │
│   ├── communication/                 # Communication layer (12 files)
│   │   ├── __init__.py
│   │   ├── websocket/
│   │   │   ├── ws_client.py           # WebSocket client
│   │   │   ├── ws_handler.py          # Message handling
│   │   │   ├── ws_events.py           # Event definitions
│   │   │   └── ws_serializer.py       # JSON serialization
│   │   │
│   │   ├── streaming/
│   │   │   ├── stream_handler.py      # Streaming protocol
│   │   │   ├── delta_processor.py     # Delta aggregation
│   │   │   └── response_builder.py    # Response assembly
│   │   │
│   │   └── voice/
│   │       ├── audio_input.py         # Microphone capture
│   │       ├── audio_output.py        # Speaker playback
│   │       └── audio_processor.py     # PCM processing
│   │
│   ├── prompts/                       # Prompt management (8 files)
│   │   ├── __init__.py
│   │   ├── prompt_loader.py           # Template loading
│   │   ├── prompt_renderer.py         # Variable substitution
│   │   ├── prompt_cache.py            # Caching layer
│   │   └── templates/
│   │       ├── orchestrator_prompt.md
│   │       ├── claude_system_prompt.md
│   │       └── claude_onboarding.md
│   │
│   ├── storage/                       # Persistence layer (8 files)
│   │   ├── __init__.py
│   │   ├── registry_store.py          # JSON registry
│   │   ├── session_store.py           # Session persistence
│   │   ├── operator_store.py          # Operator files
│   │   ├── screenshot_store.py        # Screenshot mgmt
│   │   └── lock_manager.py            # Thread-safe locks
│   │
│   ├── observability/                 # Monitoring (6 files)
│   │   ├── __init__.py
│   │   ├── event_logger.py            # Event logging
│   │   ├── cost_tracker.py            # Token/cost tracking
│   │   ├── metrics_collector.py       # Metrics aggregation
│   │   └── webhook_sender.py          # Observability HTTP
│   │
│   ├── ui/                            # User interface (6 files)
│   │   ├── __init__.py
│   │   ├── console_ui.py              # Rich console
│   │   ├── panel_renderer.py          # Panel formatting
│   │   └── input_handler.py           # User input
│   │
│   └── utils/                         # Utilities (8 files)
│       ├── __init__.py
│       ├── logger.py                  # Logging setup
│       ├── validators.py              # Input validation
│       ├── formatters.py              # Data formatting
│       └── exceptions.py              # Custom exceptions
│
├── agentpool/                         # 150+ specialized agents
│   ├── README.md
│   ├── backend-architect.md
│   ├── frontend-architect.md
│   ├── devops-architect.md
│   ├── security-engineer.md
│   ├── performance-engineer.md
│   └── ... (145+ more agents)
│
├── config/                            # Configuration files
│   ├── default.yaml                   # Default settings
│   ├── agents.yaml                    # Agent configurations
│   ├── tools.yaml                     # Tool configurations
│   └── models.yaml                    # Model settings
│
├── apps/
│   ├── content-gen/                   # Agent working directory
│   └── realtime-poc/                  # Legacy (to be removed)
│
├── tests/                             # Test suite
│   ├── unit/                          # Unit tests
│   ├── integration/                   # Integration tests
│   └── fixtures/                      # Test fixtures
│
├── docs/                              # Documentation
│   ├── architecture.md
│   ├── agent_development.md
│   └── api_reference.md
│
├── scripts/                           # Utility scripts
│   ├── setup.sh                       # Environment setup
│   └── migrate.py                     # Migration script
│
├── main.py                            # Application entry point <150 lines
├── pyproject.toml                     # Dependencies
├── .env.sample                        # Environment template
└── README.md                          # Project documentation
```

**File Count Summary:**
- Core: ~10 files
- Agents: ~15 files
- Tools: ~20 files
- Communication: ~12 files
- Prompts: ~8 files
- Storage: ~8 files
- Observability: ~6 files
- UI: ~6 files
- Utils: ~8 files
- **Total: ~93 modular files** (all <150 lines)

---

## 3. Core Components Design

### 3.1 Orchestrator (src/core/orchestrator.py)

**Responsibility**: Central coordination of agents and tools

**Key Methods:**
```python
class Orchestrator:
    """Main system coordinator (<150 lines)"""

    def __init__(self, config: Config):
        self.config = config
        self.session_manager = SessionManager()
        self.agent_registry = AgentRegistry()
        self.tool_registry = ToolRegistry()
        self.event_bus = EventBus()

    async def start(self) -> None:
        """Initialize system components"""

    async def handle_request(self, request: Request) -> Response:
        """Route request to appropriate handler"""

    async def shutdown(self) -> None:
        """Graceful shutdown"""
```

**Line Budget: ~120 lines**
- Initialization: 30 lines
- Request routing: 40 lines
- Event handling: 30 lines
- Lifecycle: 20 lines

---

### 3.2 Agent Management (src/agents/base/agent_registry.py)

**Responsibility**: Agent lifecycle and registration

**Key Methods:**
```python
class AgentRegistry:
    """Thread-safe agent registry (<150 lines)"""

    def register(self, agent: Agent) -> None:
        """Register new agent"""

    def get(self, agent_name: str) -> Optional[Agent]:
        """Retrieve agent by name"""

    def list_all(self) -> List[Agent]:
        """List all registered agents"""

    def unregister(self, agent_name: str) -> None:
        """Remove agent from registry"""
```

**Line Budget: ~100 lines**
- Registration: 25 lines
- Lookup: 20 lines
- Listing: 15 lines
- Persistence: 40 lines

---

### 3.3 Tool System (src/tools/base/tool_executor.py)

**Responsibility**: Tool execution with error handling

**Key Methods:**
```python
class ToolExecutor:
    """Execute tools with proper error handling (<150 lines)"""

    async def execute(self, tool_name: str, args: dict) -> dict:
        """Execute tool with arguments"""

    def register_tool(self, tool: Tool) -> None:
        """Register tool in system"""

    def build_tool_specs(self) -> List[dict]:
        """Build OpenAI function specs"""
```

**Line Budget: ~130 lines**
- Execution: 50 lines
- Registration: 30 lines
- Spec building: 30 lines
- Error handling: 20 lines

---

### 3.4 Communication Layer (src/communication/websocket/ws_client.py)

**Responsibility**: WebSocket connection management

**Key Methods:**
```python
class WebSocketClient:
    """OpenAI Realtime API client (<150 lines)"""

    async def connect(self) -> None:
        """Establish WebSocket connection"""

    async def send_event(self, event: Event) -> None:
        """Send event to server"""

    async def receive_event(self) -> Event:
        """Receive event from server"""

    async def disconnect(self) -> None:
        """Close connection"""
```

**Line Budget: ~120 lines**
- Connection: 30 lines
- Send/receive: 40 lines
- Event parsing: 30 lines
- Error handling: 20 lines

---

## 4. Agent Pool Integration

### 4.1 Pool Manager Design

**Location**: src/agents/pool/pool_manager.py

**Purpose**: Dynamic loading and selection of 150+ specialized agents

**Architecture:**
```python
class AgentPoolManager:
    """Manage 150+ specialized agents (<150 lines)"""

    def __init__(self, pool_dir: Path):
        self.pool_dir = pool_dir
        self.loader = PoolLoader(pool_dir)
        self.selector = PoolSelector()
        self.cache = {}

    def load_agent(self, agent_type: str) -> AgentSpec:
        """Load agent specification from pool"""

    def select_agent(self, task: str) -> str:
        """Select best agent for task"""

    def list_available(self) -> List[str]:
        """List all available agents"""
```

**Line Budget: ~140 lines**
- Loading: 40 lines
- Selection: 50 lines
- Caching: 30 lines
- Utils: 20 lines

---

### 4.2 Agent Pool Structure

Each agent in agentpool/ follows standard format:

```markdown
# Agent Name

**Role**: Specific expertise

**Triggers**:
- Keyword patterns
- Task types
- Context indicators

**Capabilities**:
- Capability 1
- Capability 2
- Capability 3

**Tools**: Required tool list

**Prompts**: Agent-specific prompts

**Examples**: Usage examples
```

**Integration Pattern:**
1. Task arrives at orchestrator
2. PoolSelector analyzes task requirements
3. PoolLoader retrieves agent specification
4. Agent instantiated with spec + base agent class
5. Agent executes with specialized prompts/tools

---

## 5. Communication Flow Design

### 5.1 Request Processing Flow

```
User Input (Voice/Text)
    ↓
┌─────────────────────────────────────────┐
│ WebSocketClient receives                │
│ - audio/text input                      │
│ - OpenAI processes                      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ EventBus dispatches                     │
│ - function_call_arguments.delta         │
│ - DeltaProcessor aggregates             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Orchestrator routes                     │
│ - Parses completed arguments            │
│ - Selects tool/agent                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ ToolExecutor executes                   │
│ - Validates arguments                   │
│ - Calls appropriate handler             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Agent performs work                     │
│ - ClaudeAgent / GeminiAgent             │
│ - Uses specialized tools                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ ObservabilityLogger records             │
│ - Events, metrics, costs                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ WebSocketClient sends result            │
│ - function_call_output                  │
│ - OpenAI generates response             │
└─────────────────────────────────────────┘
    ↓
User Output (Voice/Text)
```

### 5.2 Event System Design

**Event Types:**
```python
class EventType(Enum):
    # WebSocket events
    SESSION_UPDATE = "session.update"
    INPUT_AUDIO = "input_audio_buffer.append"
    FUNCTION_CALL_DELTA = "response.function_call_arguments.delta"
    RESPONSE_DONE = "response.done"

    # Internal events
    AGENT_CREATED = "agent.created"
    AGENT_COMMAND = "agent.command"
    TOOL_EXECUTE = "tool.execute"
    TASK_COMPLETE = "task.complete"
```

**Event Bus Implementation**: src/core/event_bus.py
- Pub/sub pattern
- Async event dispatch
- Typed events with validation
- <150 lines

---

## 6. Configuration Management

### 6.1 Configuration Files

**config/default.yaml:**
```yaml
system:
  name: "Big Three Realtime Agents"
  version: "2.0.0"
  engineer_name: "${ENGINEER_NAME}"

orchestrator:
  model: "gpt-4-realtime-preview-2024-12-17"
  voice: "shimmer"
  tool_choice: "auto"

agents:
  working_directory: "apps/content-gen"
  claude:
    model: "claude-sonnet-4-5-20250929"
    max_tokens: 8192
  gemini:
    model: "gemini-2.0-flash-exp"
    screen_resolution: [1440, 900]
    max_automation_turns: 30

tools:
  enabled:
    - list_agents
    - create_agent
    - command_agent
    - check_agent_result
    - delete_agent
    - browser_use
    - read_file
    - open_file
    - report_costs

observability:
  enabled: true
  webhook_url: "http://localhost:3000/api/claude-code-hooks"
  log_level: "INFO"

storage:
  registry_path: "apps/content-gen/agents"
  screenshots_path: "apps/content-gen/screenshots"
```

**config/agents.yaml:**
```yaml
agent_pool:
  directory: "agentpool"
  auto_load: true
  selection_strategy: "best_match"

agent_types:
  - name: "backend-architect"
    triggers: ["backend", "api", "server", "database"]
    priority: 10

  - name: "frontend-architect"
    triggers: ["frontend", "ui", "react", "vue"]
    priority: 10

  # ... 148+ more agents
```

### 6.2 Config Loader (src/core/config_loader.py)

```python
class ConfigLoader:
    """Load and validate configuration (<150 lines)"""

    def load(self, config_path: Path) -> Config:
        """Load configuration from YAML"""

    def merge(self, *configs: Config) -> Config:
        """Merge multiple configs"""

    def validate(self, config: Config) -> None:
        """Validate configuration"""
```

**Line Budget: ~100 lines**

---

## 7. Implementation Strategy

### 7.1 Phase 1: Core Infrastructure (Week 1)
- ✅ Directory structure setup
- ✅ Core orchestrator skeleton
- ✅ Event bus implementation
- ✅ Configuration system
- ✅ Base classes and interfaces

### 7.2 Phase 2: Agent System (Week 2)
- ✅ Agent registry and lifecycle
- ✅ Claude agent wrapper
- ✅ Gemini agent wrapper
- ✅ Agent pool integration
- ✅ Session management

### 7.3 Phase 3: Tool System (Week 3)
- ✅ Tool registry and executor
- ✅ 9 core tools implementation
- ✅ Agent-specific tools
- ✅ Tool spec builder

### 7.4 Phase 4: Communication (Week 4)
- ✅ WebSocket client
- ✅ Event handlers
- ✅ Streaming system
- ✅ Voice I/O

### 7.5 Phase 5: Integration (Week 5)
- ✅ End-to-end testing
- ✅ Observability system
- ✅ UI/UX polish
- ✅ Documentation

### 7.6 Phase 6: Migration (Week 6)
- ✅ Data migration from old system
- ✅ Backward compatibility
- ✅ Performance testing
- ✅ Production deployment

---

## 8. Module Specifications

### 8.1 Core Modules (<150 lines each)

| Module | Lines | Responsibility |
|--------|-------|----------------|
| orchestrator.py | 120 | Main coordination |
| session_manager.py | 100 | Session lifecycle |
| event_bus.py | 130 | Event distribution |
| config_loader.py | 100 | Config management |

### 8.2 Agent Modules

| Module | Lines | Responsibility |
|--------|-------|----------------|
| agent_interface.py | 80 | Base contract |
| agent_registry.py | 100 | Registration |
| claude_agent.py | 140 | Claude wrapper |
| claude_factory.py | 120 | Agent creation |
| gemini_agent.py | 140 | Gemini wrapper |
| gemini_browser.py | 130 | Browser control |
| pool_manager.py | 140 | Pool coordination |

### 8.3 Tool Modules

| Module | Lines | Responsibility |
|--------|-------|----------------|
| tool_interface.py | 60 | Tool contract |
| tool_executor.py | 130 | Execution engine |
| list_agents.py | 80 | Agent listing |
| create_agent.py | 120 | Agent creation |
| command_agent.py | 140 | Agent command |
| browser_use.py | 140 | Browser automation |

### 8.4 Communication Modules

| Module | Lines | Responsibility |
|--------|-------|----------------|
| ws_client.py | 120 | WebSocket client |
| ws_handler.py | 140 | Message handling |
| delta_processor.py | 100 | Delta aggregation |
| audio_input.py | 130 | Mic capture |
| audio_output.py | 130 | Speaker output |

---

## 9. Quality Standards

### 9.1 Code Quality Metrics

**Per-File Standards:**
- Maximum lines: 150
- Maximum function length: 30 lines
- Maximum complexity: 10 (McCabe)
- Minimum test coverage: 80%
- Type hints: Required
- Docstrings: Required

**Project Standards:**
- Total files: ~100 modules
- Test files: 1:1 ratio with source
- Documentation: Comprehensive
- Dependencies: Minimal

### 9.2 Testing Strategy

```
tests/
├── unit/                    # Unit tests (1:1 with src/)
│   ├── test_orchestrator.py
│   ├── test_agent_registry.py
│   └── test_tool_executor.py
│
├── integration/             # Integration tests
│   ├── test_claude_workflow.py
│   ├── test_gemini_workflow.py
│   └── test_full_pipeline.py
│
└── fixtures/                # Test data
    ├── mock_agents.yaml
    └── sample_sessions.json
```

### 9.3 Performance Targets

- Agent creation: <2 seconds
- Tool execution: <500ms (excluding agent work)
- WebSocket latency: <100ms
- Memory per agent: <50MB
- Concurrent agents: 10+

---

## 10. Migration Path

### 10.1 Backward Compatibility

**Registry Format:**
- Maintain JSON registry structure
- Add migration layer for old sessions
- Support gradual migration

**API Compatibility:**
- Keep same tool names/signatures
- Preserve operator file format
- Maintain screenshot storage

### 10.2 Migration Script

```python
# scripts/migrate.py
class SystemMigrator:
    """Migrate from old to new system"""

    def migrate_registry(self):
        """Convert old registry to new format"""

    def migrate_sessions(self):
        """Migrate active sessions"""

    def migrate_operators(self):
        """Move operator files"""
```

### 10.3 Rollback Plan

- Keep old system in apps/realtime-poc/
- Symlink for easy switching
- Data backup before migration
- Validation tests

---

## 11. Documentation Requirements

### 11.1 Developer Documentation

**docs/architecture.md:**
- System overview
- Component interactions
- Data flows
- Extension points

**docs/agent_development.md:**
- How to add new agents
- Agent specification format
- Testing guidelines
- Best practices

**docs/api_reference.md:**
- Public API documentation
- Tool specifications
- Event reference
- Configuration options

### 11.2 User Documentation

**README.md:**
- Quick start guide
- Installation instructions
- Basic usage examples
- Troubleshooting

**docs/user_guide.md:**
- Advanced usage
- Agent pool overview
- Voice commands
- Best practices

---

## 12. Success Criteria

### 12.1 Functional Requirements

✅ All 9 core tools working
✅ Claude Code agent integration
✅ Gemini browser automation
✅ Voice input/output
✅ 150+ agent pool accessible
✅ Session persistence
✅ Observability system

### 12.2 Non-Functional Requirements

✅ All files <150 lines
✅ 80%+ test coverage
✅ <2s agent creation time
✅ Comprehensive documentation
✅ Type safety with mypy
✅ Clean linting (ruff/black)

### 12.3 Quality Gates

- All tests pass
- Type checking passes
- Linting passes
- Documentation complete
- Performance benchmarks met
- Security scan clean

---

## 13. Next Steps

### 13.1 Immediate Actions

1. **Setup infrastructure**
   - Create directory structure
   - Setup pyproject.toml
   - Initialize git structure

2. **Implement core layer**
   - Orchestrator skeleton
   - Event bus
   - Config loader

3. **Base classes**
   - Agent interface
   - Tool interface
   - Event types

### 13.2 Development Workflow

```bash
# 1. Create branch
git checkout -b refactor/modular-architecture

# 2. Implement module
vim src/core/orchestrator.py

# 3. Write tests
vim tests/unit/test_orchestrator.py

# 4. Validate
ruff check src/
mypy src/
pytest tests/

# 5. Commit
git add . && git commit -m "feat(core): implement orchestrator"
```

### 13.3 Review Points

- After each phase completion
- Before merging to main
- Performance benchmarks
- User acceptance testing

---

## 14. Risk Mitigation

### 14.1 Technical Risks

**Risk**: Breaking changes during refactor
**Mitigation**: Parallel systems, gradual migration

**Risk**: Performance degradation
**Mitigation**: Benchmarking, profiling, optimization

**Risk**: Complex debugging across modules
**Mitigation**: Comprehensive logging, observability

### 14.2 Timeline Risks

**Risk**: Scope creep
**Mitigation**: Strict phase boundaries, MVP focus

**Risk**: Dependencies blocked
**Mitigation**: Parallel development, mocking

---

## Appendix A: File Size Guidelines

**How to keep files <150 lines:**

1. **Single Responsibility**: One class/function per file
2. **Extraction**: Move utilities to separate files
3. **Composition**: Prefer composition over inheritance
4. **Configuration**: Externalize settings
5. **Documentation**: Use separate docs/ files
6. **Testing**: Separate test files

**Example Refactoring:**

❌ **Bad**: 300-line agent.py
```python
class Agent:
    # 300 lines of mixed concerns
```

✅ **Good**: Split into 3 files
```python
# agent_base.py (100 lines)
# agent_factory.py (80 lines)
# agent_tools.py (120 lines)
```

---

## Appendix B: Dependency Graph

```
main.py
  └─> Orchestrator
       ├─> SessionManager
       ├─> AgentRegistry
       │    ├─> ClaudeAgent
       │    ├─> GeminiAgent
       │    └─> PoolManager
       ├─> ToolRegistry
       │    └─> ToolExecutor
       ├─> EventBus
       └─> WebSocketClient
            ├─> AudioInput
            └─> AudioOutput
```

**Dependency Rules:**
- No circular dependencies
- One-way flow (top to bottom)
- Interface-based coupling
- Dependency injection

---

## Appendix C: Technology Stack

**Core:**
- Python 3.11+
- asyncio for concurrency
- pydantic for validation
- typing for type safety

**Communication:**
- websocket-client for OpenAI
- pyaudio for voice I/O

**Agents:**
- claude-agent-sdk for Claude
- google-genai for Gemini
- playwright for browser

**Storage:**
- JSON for registries
- YAML for configuration
- Markdown for operators

**Development:**
- pytest for testing
- ruff for linting
- mypy for type checking
- black for formatting

**Documentation:**
- mkdocs for docs
- docstrings for API
- mermaid for diagrams

---

## Summary

This refactoring design transforms the 3,228-line monolithic system into a clean, modular architecture with:

✅ **~100 files, all <150 lines**
✅ **Clear separation of concerns**
✅ **150+ agent pool integration**
✅ **Scalable and maintainable**
✅ **Comprehensive testing**
✅ **Production-ready quality**

The design maintains all existing functionality while enabling future extensibility through the agent pool system and plugin architecture.

**Estimated Implementation:** 6 weeks with 1 developer
**Complexity:** High (architectural refactor)
**Risk Level:** Medium (with proper testing and migration)
**Impact:** High (foundation for future growth)
