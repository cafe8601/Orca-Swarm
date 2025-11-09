# 📊 Observability System Guide

**Purpose**: Real-time monitoring and visualization of multi-agent activities

**Status**: ✅ Fully Integrated

---

## 🎯 Overview

The Observability System provides **real-time monitoring** of all Claude Code agent activities through a beautiful web dashboard.

**What You Can See**:
- ✅ Real-time event timeline
- ✅ Multi-agent session tracking
- ✅ Tool usage monitoring
- ✅ Performance metrics
- ✅ Chat transcripts
- ✅ Error tracking
- ✅ Activity charts

**Architecture**:
```
Claude Code Agent → Hooks → HTTP → Server → WebSocket → Dashboard
                              ↓
                         SQLite DB
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Start observability services
docker compose up -d observability-server observability-client

# Open dashboard
open http://localhost:5173

# Run Claude Code in this project
# Events will automatically appear in the dashboard!
```

### Option 2: Native (Bun Required)

```bash
# Install Bun first: https://bun.sh
curl -fsSL https://bun.sh/install | bash

# Start observability system
./scripts/start-observability.sh

# Open dashboard
open http://localhost:5173
```

---

## 📊 Dashboard Features

### 1. **Real-Time Event Timeline**

See all agent activities as they happen:
- 🔧 Tool usage (Read, Write, Edit, Bash, etc.)
- 💬 User prompts
- ✅ Tool results
- 🔔 Notifications
- 📝 Session events

### 2. **Multi-Agent Session Tracking**

Monitor multiple agents simultaneously:
- Different colors per agent
- Session-based grouping
- Filter by agent/session
- Historical playback

### 3. **Event Filtering**

Focus on what matters:
- Filter by event type
- Filter by session
- Filter by agent
- Search functionality
- Time range selection

### 4. **Live Activity Charts**

Visual performance metrics:
- Events per minute
- Tool usage distribution
- Agent activity levels
- Error rates

### 5. **Chat Transcript Viewer**

Review full conversations:
- Complete chat history
- User prompts
- Agent responses
- Tool interactions
- Export capability

---

## 🔧 Configuration

### Hook System (.claude/settings.json)

Already configured for `multi-agent-learning` project:

```json
{
  "hooks": {
    "PreToolUse": [...],    // Before tool execution
    "PostToolUse": [...],   // After tool execution
    "UserPromptSubmit": [...], // User input
    "Notification": [...],  // System notifications
    "Stop": [...],         // Session end
    "SubagentStop": [...], // Subagent completion
    "PreCompact": [...],   // Context compression
    "SessionStart": [...], // Session begin
    "SessionEnd": [...]    // Session end
  }
}
```

**Source App ID**: `multi-agent-learning` (identifies this project)

---

## 🔌 API Endpoints

### Server (Port 4000)

**HTTP Endpoints**:
- `POST /events` - Ingest hook events
- `GET /events` - Query events
- `GET /events/filter-options` - Get available filters
- `GET /health` - Health check

**WebSocket**:
- `ws://localhost:4000/stream` - Real-time event streaming

---

## 📁 Components

### 1. Hooks (.claude/hooks/)

**10 Hook Scripts**:
```
✅ pre_tool_use.py       # Validate tool usage
✅ post_tool_use.py      # Capture results
✅ user_prompt_submit.py # Log user input
✅ notification.py       # Track notifications
✅ stop.py              # Session completion
✅ subagent_stop.py     # Subagent tracking
✅ pre_compact.py       # Context management
✅ session_start.py     # Session initialization
✅ session_end.py       # Session finalization
✅ send_event.py        # Universal event sender
```

**Utils**:
```
✅ summarizer.py        # AI-powered event summarization
✅ constants.py         # Configuration
✅ tts/ (optional)      # Text-to-speech
✅ llm/ (optional)      # LLM integrations
```

### 2. Server (apps/observability-server/)

**Technology**: Bun + TypeScript

**Features**:
- HTTP API for event ingestion
- WebSocket for real-time streaming
- SQLite database for persistence
- Event filtering and querying
- Automatic database migrations

**Files**:
```
src/
├── index.ts    # Main server
├── db.ts       # Database management
└── types.ts    # TypeScript interfaces
```

### 3. Client (apps/observability-client/)

**Technology**: Vue 3 + TypeScript + Vite

**Features**:
- Real-time dashboard
- Event timeline with auto-scroll
- Multi-select filtering
- Live activity charts
- Chat transcript modal
- Dark/light theme
- Responsive design

**Files**:
```
src/
├── App.vue                 # Main application
├── components/
│   ├── EventTimeline.vue   # Event list
│   ├── EventRow.vue        # Individual events
│   ├── FilterPanel.vue     # Filters
│   ├── ChatTranscriptModal.vue # Chat viewer
│   ├── StickScrollButton.vue   # Scroll control
│   └── LivePulseChart.vue      # Activity chart
└── composables/
    ├── useWebSocket.ts     # WebSocket logic
    ├── useEventColors.ts   # Color system
    └── useChartData.ts     # Chart aggregation
```

---

## 🎬 Usage Scenarios

### Scenario 1: Debugging Multi-Agent Workflow

```bash
# 1. Start observability
./scripts/start-observability.sh

# 2. Open dashboard
open http://localhost:5173

# 3. Run multi-agent task
python -m apps.realtime-poc.big_three_realtime_agents.main \
  --prompt "Create a web app"

# 4. Watch in real-time:
#    - OpenAI Orchestrator decisions
#    - Claude Code agent execution
#    - Gemini Browser automation
#    - Agent Pool allocations
```

### Scenario 2: Performance Analysis

```bash
# 1. Dashboard open
# 2. Run multiple tasks
# 3. Analyze:
#    - Tool usage patterns
#    - Execution times
#    - Bottlenecks
#    - Error rates
```

### Scenario 3: Learning from History

```bash
# 1. Complete several tasks
# 2. Review chat transcripts
# 3. Analyze successful patterns
# 4. Optimize workflows
```

---

## 🐳 Docker Deployment

### Start All Services

```bash
# Start everything (main system + observability)
docker compose up -d

# Services started:
# - big-three-agents (main application)
# - redis (caching)
# - observability-server (event ingestion)
# - observability-client (dashboard)
```

### Start Observability Only

```bash
# Just observability (if main system runs separately)
docker compose up -d observability-server observability-client
```

### Monitor Logs

```bash
# Server logs
docker compose logs -f observability-server

# Client logs
docker compose logs -f observability-client

# All observability logs
docker compose logs -f observability-server observability-client
```

### Stop Services

```bash
# Stop observability
docker compose stop observability-server observability-client

# Or stop everything
docker compose down
```

---

## 🔧 Troubleshooting

### Issue: Dashboard shows "Connecting..."

**Problem**: Server not running or not accessible

**Solution**:
```bash
# Check if server is running
curl http://localhost:4000/health

# Check Docker logs
docker compose logs observability-server

# Restart server
docker compose restart observability-server
```

---

### Issue: No events appearing

**Problem**: Hooks not sending events

**Solution**:
```bash
# 1. Verify hooks are configured
cat .claude/settings.json

# 2. Test hook manually
uv run .claude/hooks/send_event.py --source-app multi-agent-learning --event-type Test

# 3. Check server logs
docker compose logs -f observability-server

# 4. Verify server is accessible
curl -X POST http://localhost:4000/events \
  -H "Content-Type: application/json" \
  -d '{"test": "event"}'
```

---

### Issue: Port already in use

**Problem**: 4000 or 5173 already taken

**Solution**:
```bash
# Check what's using ports
lsof -i :4000
lsof -i :5173

# Kill processes or change ports in docker-compose.yml
```

---

## 📈 Advanced Usage

### Event Summarization

Hooks support AI-powered event summarization:

```bash
# Enable summarization (already enabled in settings.json)
--summarize flag in send_event.py

# Requires ANTHROPIC_API_KEY in .env
```

### Chat History

Include full chat transcripts:

```bash
# Add --add-chat flag (already in Stop hook)
# See complete conversation context
```

### Custom Event Types

Add custom hooks for specific events:

```json
{
  "YourCustomEvent": [{
    "hooks": [{
      "type": "command",
      "command": "uv run .claude/hooks/send_event.py --source-app multi-agent-learning --event-type YourCustomEvent"
    }]
  }]
}
```

---

## 🎯 Integration with Big Three Agents

### How It Works

```
User Input
    ↓
OpenAI Orchestrator (monitored)
    ↓
    ├─→ Claude Code Agent (hooks capture everything)
    │       ↓
    │   Tool Usage → Dashboard shows:
    │       - Which files read/written
    │       - Commands executed
    │       - Results
    │       - Errors
    │
    └─→ Gemini Browser (monitored indirectly)
            ↓
        Browser Actions → Logged via Claude

All visible in real-time on dashboard!
```

### Multi-Agent Visibility

```
Dashboard shows:
- OpenAI orchestrator decisions
- Claude Code operations
- Agent Pool allocations
- Tool execution results
- Session management
- Error tracking
- Performance metrics
```

---

## 📚 Additional Resources

### Documentation
- **Main README**: Project overview
- **DEPLOYMENT_GUIDE**: Full deployment guide
- **This Guide**: Observability specific

### Source Project
- Original: https://github.com/disler/claude-code-hooks-multi-agent-observability
- Video: https://youtu.be/9ijnN985O_c

### Claude Code Hooks
- Docs: https://docs.anthropic.com/en/docs/claude-code/hooks
- Mastery: https://github.com/disler/claude-code-hooks-mastery

---

## 🎉 Quick Reference

### Start Observability
```bash
# Docker
docker compose up -d observability-server observability-client

# Native
./scripts/start-observability.sh
```

### Access Dashboard
```
http://localhost:5173
```

### Check Server
```
http://localhost:4000/health
```

### Stop Observability
```bash
# Docker
docker compose stop observability-server observability-client

# Native
# Press Ctrl+C in terminal running start-observability.sh
```

---

**Version**: 1.0 (Integrated)
**Last Updated**: 2025-11-09
**Integration**: Complete
