# Document 2 — System Architecture Design

---

## 2.1 Architecture Philosophy

The architecture is built on three principles:

1. **Event-Driven, Not Request-Driven**: Agents react to state changes, not just user clicks. When an organizer uploads a CSV, the system doesn't wait for a "process" button — it autonomously begins extraction, validation, and segmentation.

2. **Thin Orchestration, Fat Agents**: The orchestrator (LangGraph) handles routing and state transitions. The actual intelligence lives inside each agent's specialized logic. This keeps the system debuggable and modular.

3. **Observable by Default**: Every action, decision, and inter-agent message is logged and streamable to the frontend. The architecture is instrumented from day one, not as an afterthought.

---

## 2.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Dashboard │ │ Schedule │ │ Content  │ │  Mail    │ │  Agent   │ │
│  │ Overview  │ │  View    │ │  Studio  │ │  Center  │ │ Activity │ │
│  └─────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│        └────────────┴────────────┴────────────┴────────────┘       │
│                             │  WebSocket + REST                     │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                      │
│                              │                                      │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                    API Gateway Layer                           │  │
│  │  REST Endpoints │ WebSocket Manager │ File Upload Handler     │  │
│  └───────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │              ORCHESTRATOR (LangGraph State Machine)            │  │
│  │                                                               │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │  │
│  │  │   Router     │  │  State Mgr   │  │  Event Dispatcher   │  │  │
│  │  │  (decides    │  │  (shared     │  │  (triggers agents   │  │  │
│  │  │   which      │  │   graph      │  │   on state changes) │  │  │
│  │  │   agent)     │  │   state)     │  │                     │  │  │
│  │  └──────┬──────┘  └──────┬───────┘  └──────────┬──────────┘  │  │
│  │         └────────────────┴──────────────────────┘             │  │
│  └───────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
│  ┌───────────┬───────────────┼────────────────┬──────────────────┐  │
│  │           │               │                │                  │  │
│  ▼           ▼               ▼                ▼                  ▼  │
│ ┌─────┐  ┌──────┐    ┌───────────┐    ┌───────────┐   ┌────────┐  │
│ │Sched│  │ Mail │    │  Content  │    │ Analytics │   │  Meta  │  │
│ │uler │  │Agent │    │  Agent    │    │  Agent    │   │ Agent  │  │
│ │Agent│  │      │    │           │    │ (innov.)  │   │(innov.)│  │
│ └──┬──┘  └──┬───┘    └─────┬─────┘    └─────┬─────┘   └───┬────┘  │
│    │        │              │                │             │        │
│  ┌─┴────────┴──────────────┴────────────────┴─────────────┴─────┐  │
│  │                    SHARED DATA LAYER                          │  │
│  │  ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌──────────────┐ │  │
│  │  │ Event    │ │ Participant│ │ Schedule   │ │ Agent Memory │ │  │
│  │  │ Config   │ │ Registry  │ │ Timeline   │ │ & Logs       │ │  │
│  │  └──────────┘ └───────────┘ └────────────┘ └──────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   EXTERNAL INTEGRATIONS                      │   │
│  │  LLM API (Gemini/OpenAI) │ SMTP Service │ (opt.) Social API │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2.3 Component Breakdown

### 2.3.1 Frontend — React + Vite

**Why React + Vite:**
- Your two web devs likely already know React
- Vite gives instant hot-reload for rapid hackathon iteration
- Rich ecosystem for charts (Recharts), drag-and-drop (dnd-kit), and real-time UI

**Key Frontend Modules:**

| Module | Purpose |
|---|---|
| **Dashboard Overview** | Bird's-eye view: event status, agent activity feed, key metrics |
| **Schedule View** | Interactive Gantt-style timeline with drag-and-drop, conflict highlights |
| **Content Studio** | View/edit/approve generated social media and promotional content |
| **Mail Center** | Upload CSV, preview personalized emails, approve batch sends |
| **Agent Activity Panel** | Real-time log of agent actions, inter-agent messages, reasoning traces |

**Real-Time Communication:**
- **WebSocket** connection to backend for live agent activity streaming
- REST APIs for CRUD operations (create event, upload data, approve actions)

### 2.3.2 Backend — FastAPI (Python)

**Why FastAPI:**
- Native async support — critical for concurrent agent execution
- WebSocket support built-in
- Easy to set up in a hackathon (minimal boilerplate)
- Python ecosystem aligns with AI/ML libraries

**Backend Layers:**

#### API Gateway Layer
```python
# Responsibilities:
# 1. REST endpoints for frontend CRUD
# 2. WebSocket manager for real-time streaming
# 3. File upload handler (CSV/Excel processing)
# 4. Authentication (simple token-based for hackathon)
```

#### Orchestrator Layer (LangGraph)
This is the brain. It's a **state machine** that:
- Receives events (user actions, data uploads, timer triggers)
- Decides which agent(s) to activate
- Manages the shared graph state
- Handles inter-agent communication
- Streams decisions to the frontend via WebSocket

#### Agent Layer
Each agent is an **independent module** with:
- Its own system prompt and tools
- Access to shared state (read/write)
- The ability to emit events that trigger other agents
- Structured output schemas for consistent data handling

#### Shared Data Layer
- **In-memory state** (Python dict / LangGraph state) for fast access during hackathon
- **SQLite** or **JSON file** persistence for durability across server restarts
- Structured schemas for event config, participant data, schedules, and agent logs

### 2.3.3 LLM Integration

**Primary: Google Gemini API (gemini-2.0-flash)**
- Free tier is generous, fast, and good enough for all agent tasks
- Structured output support (JSON mode) for reliable agent responses
- Long context window for processing large CSVs

**Fallback: OpenAI GPT-4o-mini**
- If Gemini rate-limits during demo, switch seamlessly
- Both APIs have compatible interfaces via LangChain/LiteLLM

**Usage pattern:**
- Each agent call is a single LLM invocation with specific tools and system prompt
- No fine-tuning needed — prompt engineering is sufficient for hackathon scope
- Structured output (Pydantic models) ensures agents return usable data, not free-form text

---

## 2.4 Data Flow — The Lifecycle of a Request

### Example: Organizer uploads a registration CSV

```
1. FRONTEND: User drops CSV in Mail Center
        │
        ▼
2. API GATEWAY: POST /upload/participants
   - Validates file type
   - Stores file temporarily
   - Emits event: PARTICIPANT_DATA_UPLOADED
        │
        ▼
3. ORCHESTRATOR: Receives PARTICIPANT_DATA_UPLOADED
   - Updates graph state: participants_raw = <file_path>
   - Routes to: Mail Agent (primary), Analytics Agent (secondary)
        │
        ├──────────────────────────────┐
        ▼                              ▼
4a. MAIL AGENT:                   4b. ANALYTICS AGENT:
    - Parses CSV                      - Counts registrants
    - Extracts emails                 - Builds demographic
    - Validates format                  breakdown
    - Segments by criteria            - Updates dashboard
    - Stores clean data                 metrics
    - Emits: PARTICIPANTS_PROCESSED
        │
        ▼
5. ORCHESTRATOR: Receives PARTICIPANTS_PROCESSED
   - Updates state: participants_clean = [...]
   - Notifies frontend via WebSocket:
     "✅ Mail Agent processed 347 participants (12 invalid emails flagged)"
        │
        ▼
6. FRONTEND: Dashboard updates in real-time
   - Activity feed shows processing completed
   - Mail Center shows clean participant list
   - Analytics panel updates with new demographics
```

### Example: Cascading schedule change

```
1. Organizer changes "Keynote Speaker" time from 10:00 AM to 2:00 PM
        │
        ▼
2. ORCHESTRATOR emits: SCHEDULE_CONSTRAINT_CHANGED
        │
        ▼
3. SCHEDULER AGENT:
   - Detects conflict: Workshop B was at 2:00-3:00 PM in the same room
   - Resolves: Moves Workshop B to 10:00-11:00 AM (freed by keynote move)
   - Checks: No further cascading conflicts
   - Updates schedule state
   - Emits: SCHEDULE_MODIFIED {affected_sessions: [workshop_b], affected_participants: 87}
        │
        ├──────────────────────────────┐
        ▼                              ▼
4a. MAIL AGENT:                   4b. CONTENT AGENT:
    - Generates notification          - Updates any queued
      emails for 87 affected            social posts that
      participants                       mention workshop timing
    - Awaits organizer approval       - Drafts correction post
                                      - Awaits approval
        │
        ▼
5. FRONTEND: Shows pending approval cards
   - "📧 Send schedule update to 87 participants?" [Approve] [Edit] [Reject]
   - "📱 Update social post about workshop timing?" [Approve] [Edit] [Reject]
```

---

## 2.5 Technology Stack Summary

| Layer | Technology | Justification |
|---|---|---|
| Frontend | React 18 + Vite | Fast dev, team familiarity, rich ecosystem |
| UI Components | Shadcn/UI or Ant Design | Pre-built, professional-looking components |
| Real-time | WebSocket (native) | Live agent activity streaming |
| Charts | Recharts | Simple, React-native charting |
| Backend | FastAPI (Python 3.11+) | Async, WebSocket support, AI ecosystem |
| Orchestrator | LangGraph | State machine for multi-agent orchestration |
| LLM | Gemini 2.0 Flash (primary) | Free, fast, structured output |
| Data | SQLite + In-memory state | Zero setup, good enough for hackathon |
| File Processing | Pandas | CSV/Excel parsing |
| Email | SMTP (smtp4dev for demo) or Resend API | Real email sending or simulated |
| Scheduling Logic | Custom constraint solver | More impressive than using a library blindly |

---

## 2.6 Key Architectural Decisions

### Decision 1: LangGraph over CrewAI/AutoGen

**Why LangGraph:**
- **Graph-based state machine** — explicitly models agent transitions as a directed graph
- **Conditional routing** — the orchestrator can dynamically decide which agent runs next based on state
- **Built-in persistence** — state checkpointing for free
- **Streaming** — native support for streaming agent outputs to the frontend
- **Lightweight** — doesn't impose a heavy framework on top of your agents

**Why not CrewAI:**
- CrewAI is "opinionated" — it forces a specific agent definition pattern that can fight against custom logic
- Harder to implement fine-grained human-in-the-loop controls
- The "crew" metaphor makes inter-agent communication less flexible

**Why not AutoGen:**
- More complex setup for a hackathon
- Designed for conversational multi-agent, not event-driven workflows
- Heavier dependency tree

### Decision 2: WebSocket for Real-Time, Not Polling

The agent activity panel must feel *alive*. Polling every 2 seconds creates a dead, laggy experience. WebSocket pushes give instant feedback when agents complete tasks.

### Decision 3: Structured Output Everywhere

Every agent returns a **Pydantic model**, not free-form text. This ensures:
- The frontend can reliably render agent outputs
- Inter-agent communication uses typed contracts
- Errors are caught at the schema level, not in the UI

### Decision 4: SQLite, Not PostgreSQL

For a hackathon:
- Zero configuration
- Ships as a single file
- No Docker, no database server, no connection strings
- Good enough for demo-scale data (hundreds of records, not millions)

If the team wants, they can swap to PostgreSQL later, but SQLite removes an entire class of setup problems during a hackathon.

---

## 2.7 Directory Structure

```
nexus/
├── frontend/                  # React + Vite app
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Dashboard, Schedule, Mail, Content, Settings
│   │   ├── hooks/             # Custom hooks (useWebSocket, useAgentStream)
│   │   ├── services/          # API client functions
│   │   ├── store/             # State management (Zustand or Context)
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── routes/        # REST endpoints
│   │   │   └── websocket.py   # WebSocket manager
│   │   ├── agents/
│   │   │   ├── orchestrator.py    # LangGraph graph definition
│   │   │   ├── scheduler.py      # Scheduler Agent
│   │   │   ├── mailer.py         # Mail Agent
│   │   │   ├── content.py        # Content Agent
│   │   │   ├── analytics.py      # Analytics Agent (innovation)
│   │   │   └── meta_agent.py     # Meta Agent (innovation)
│   │   ├── models/            # Pydantic schemas
│   │   ├── services/          # Business logic (email sending, CSV parsing)
│   │   ├── state/             # Shared state management
│   │   └── config.py          # Configuration
│   ├── data/                  # SQLite DB, uploaded files
│   ├── requirements.txt
│   └── .env
│
├── docs/                      # These planning documents
└── README.md
```

---

## 2.8 Security and Error Handling (Hackathon-Appropriate)

- **API Key Management**: All LLM API keys in `.env`, never hardcoded
- **File Upload Validation**: Only accept CSV/Excel, max 10MB, scan for basic injection
- **Agent Error Recovery**: If an agent fails (LLM timeout, bad data), the orchestrator logs the error, notifies the frontend, and allows retry — no silent failures
- **Rate Limiting**: Simple in-memory rate limiting on LLM calls to avoid burning API credits during demo

---

*This architecture is designed to be impressive yet buildable within a hackathon timeline. The next document details what each agent actually does.*
