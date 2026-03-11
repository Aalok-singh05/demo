# Document 7 — Team Work Distribution

---

## 7.1 Team Composition Reminder

| Member | Role | Location | Primary Skills |
|---|---|---|---|
| **You (Member 1)** | Primary AI Dev + System Architect | On-site | AI agents, LangGraph, Python, system design |
| **Member 2** | Remote AI Dev | Remote | AI/ML, Python, supporting AI work |
| **Member 3** | Web Dev (Backend-leaning) | On-site | FastAPI, Python, APIs, databases |
| **Member 4** | Web Dev (Frontend-leaning) | On-site | React, Vite, CSS, UI components |

---

## 7.2 Work Allocation Strategy

The core principle: **minimize dependencies, maximize parallel work.**

Each person should be able to work independently for 2-3 hour stretches without blocking on someone else. This requires clear interface contracts upfront.

---

## 7.3 Detailed Work Assignments

### 🧠 YOU (Member 1) — AI Core & Orchestration

You are the lynchpin. Your work is the hardest to parallelize because other components depend on it. **Start immediately and unblock your team as fast as possible.**

**Phase 1 (First 2 hours): Foundation**
- Set up the project structure (backend folder)
- Define all Pydantic schemas (input/output for every agent)
- Build the LangGraph StateGraph skeleton (router → agents → evaluator → loop)
- Create mock agent functions that return hardcoded structured outputs
- Write the WebSocket manager for streaming agent activity
- **Deliverable:** A running backend that accepts API calls and returns mock agent responses via WebSocket

**Phase 2 (Hours 3–6): The Three Core Agents**
- Implement Scheduler Agent (Chronos) with real LLM calls + conflict detection
- Implement Mail Agent (Hermes) with CSV parsing + email personalization
- Implement Content Agent (Apollo) with content generation + campaign planning
- Wire all three into the LangGraph graph with proper cascading logic
- **Deliverable:** All three baseline agents functional with real LLM-powered intelligence

**Phase 3 (Hours 7–10): Innovation + Polish**
- Implement Analytics Agent (Athena) with insights
- Add the What-If simulator
- Implement the Meta-Agent / natural language command routing
- Fine-tune agent system prompts for better reasoning quality
- Add agent reasoning chains to all outputs
- **Deliverable:** Full AI system with innovation features

### 🤖 MEMBER 2 (Remote AI Dev) — AI Support & Data Processing

Remote work can be tricky — assign self-contained tasks that don't require real-time integration.

**Phase 1 (First 2 hours): Data Processing Utilities**
- Build the CSV/Excel parser service (robust, handles edge cases)
- Build the email validation service (regex + format checking)
- Build the participant segmentation logic
- Create sample datasets for testing (mock event CSVs, historical engagement data)
- **Deliverable:** A set of tested Python utility functions/modules that the agents will use

**Phase 2 (Hours 3–6): Agent Tools & Prompt Engineering**
- Write and iterate on system prompts for each agent
- Build the scheduling constraint solver (the algorithm that detects + resolves conflicts)
- Create the engagement analysis tool (pattern extraction from historical data)
- Build email template engine (placeholder parsing + personalization)
- **Deliverable:** All agent tools/functions ready for integration

**Phase 3 (Hours 7–10): Testing & Demos**
- Create end-to-end test scenarios (upload CSV → agents process → cascade notification)
- Help prepare demo data (realistic event with realistic conflicts)
- Write the "demo script" — exact steps the team will follow during the presentation
- **Deliverable:** Tested scenarios + demo playbook

**Communication protocol for remote work:**
- Shared Git repo with clear branch naming: `ai/agent-name` branches
- Async updates every 2 hours in team chat
- Pull requests with clear descriptions for code review
- Shared Google Doc for prompt engineering iterations

### ⚡ MEMBER 3 (Backend Web Dev) — API Layer & Data Persistence

**Phase 1 (First 2 hours): API Foundation**
- Set up FastAPI project with proper structure
- Create all REST endpoints (event CRUD, file upload, approval actions)
- Set up SQLite database with schemas for events, participants, schedules, content, logs
- Implement file upload handling (CSV/Excel)
- Set up CORS for frontend connection
- **Deliverable:** All API endpoints returning mock data, database ready

**Phase 2 (Hours 3–6): Integration**
- Connect API endpoints to the LangGraph orchestrator (the AI system)
- Build the WebSocket endpoint that streams agent activity to frontend
- Implement the approval workflow backend (store pending items, handle approve/reject)
- Set up SMTP email sending (or mock service for demo)
- Add error handling and logging
- **Deliverable:** Full backend connected to both AI system and serving the frontend

**Phase 3 (Hours 7–10): Polish & Reliability**
- Add rate limiting on LLM calls
- Implement proper error recovery (agent failures, LLM timeouts)
- Optimize WebSocket reconnection handling
- Help with demo preparation
- Load test with realistic data volumes
- **Deliverable:** Robust, demo-ready backend

### 🎨 MEMBER 4 (Frontend Web Dev) — Dashboard & UI

**Phase 1 (First 2 hours): UI Foundation**
- Set up React + Vite project
- Install UI component library (Shadcn/UI or Ant Design)
- Build the layout shell (sidebar navigation, top command bar, main content area)
- Implement the Dashboard page with mock data (event overview, agent status, activity feed)
- Set up WebSocket connection hook
- Set up the routing (Dashboard, Schedule, Mail, Content, Activity)
- **Deliverable:** Navigation works, Dashboard shows mock data, WebSocket connection ready

**Phase 2 (Hours 3–6): Core Pages**
- Build the Schedule View with interactive timeline/grid
- Build the Mail Center with CSV upload + email preview
- Build the Content Studio with content cards + approval flow
- Implement the Pending Approvals component (approve/edit/reject)
- Connect all pages to the backend REST API
- **Deliverable:** All pages functional with real backend data

**Phase 3 (Hours 7–10): Real-Time & Polish**
- Wire WebSocket data into the activity feed (live streaming)
- Add agent working animations and status indicators
- Build the reasoning chain visualizer
- Polish visual design (colors, spacing, typography, micro-animations)
- Ensure the "judge walk-through" flow is seamless
- **Deliverable:** Polished, impressive, demo-ready frontend

---

## 7.4 Critical Integration Points

These are the moments where team members must synchronize. Schedule these in advance:

| Checkpoint | When | Who | What |
|---|---|---|---|
| **API Contract** | Hour 1 | You + Member 3 + Member 4 | Agree on all API endpoint shapes, WebSocket message format |
| **First Integration** | Hour 3 | Member 3 + Member 4 | Frontend connects to backend, first real data flows |
| **AI Integration** | Hour 4 | You + Member 3 | LangGraph output flows through API to frontend |
| **End-to-End Test** | Hour 7 | All | Full flow: upload CSV → agent processes → cascading actions → UI updates |
| **Demo Rehearsal** | Hour 9 | All | Run through the full demo presentation |

---

## 7.5 Interface Contracts (Define These First!)

Before anyone starts coding, agree on these:

### REST API Endpoints

```
POST   /api/events              → Create/update event config
GET    /api/events/:id          → Get event details
POST   /api/upload/participants → Upload CSV
POST   /api/agents/invoke       → Send a request to the AI system
GET    /api/schedule            → Get current schedule
POST   /api/schedule/simulate   → What-if simulation
GET    /api/content             → Get content queue
POST   /api/approval/:id       → Approve/reject a pending item
GET    /api/activity            → Get activity log
WS     /ws/stream               → WebSocket for real-time updates
```

### WebSocket Message Types

```json
{"type": "agent_status", "agent": "chronos", "status": "working", "task": "..."}
{"type": "agent_complete", "agent": "chronos", "result": {...}}
{"type": "agent_message", "from": "chronos", "to": "hermes", "content": "..."}
{"type": "approval_request", "items": [...]}
{"type": "state_update", "field": "schedule", "data": {...}}
```

### Agent Response Schema

```json
{
  "agent": "chronos",
  "action": "conflict_resolution",
  "result": {...},
  "reasoning": "I moved Workshop B because...",
  "cascade_to": [{"agent": "hermes", "task": "notify", "data": {...}}],
  "requires_approval": true,
  "approval_items": [...]
}
```

---

## 7.6 Risk Mitigation

| Risk | Mitigation |
|---|---|
| Remote member loses connectivity | Pre-assign self-contained tasks, code reviewed before integration |
| LLM API rate limits during demo | Implement caching, have fallback API key, pre-compute demo results |
| Integration failures at demos | Have mock/fallback modes — if AI backend fails, frontend shows pre-loaded data |
| One agent is incomplete | Focus on making 2 agents excellent rather than 3 agents mediocre |
| UI looks unpolished | Use component library defaults — don't customize until core flows work |
| Time runs out | Prioritize: core cascade flow > scheduling > mailing > content > innovations |

---

## 7.7 Communication Plan

- **Shared repo**: GitHub with branch-per-feature
- **Chat**: WhatsApp/Discord for quick questions
- **Sync calls**: Brief 5-min standup every 2 hours
- **Screen share**: When integrating, share screens to debug together
- **Demo doc**: Shared Google Doc for the demo script, updated continuously

---

*The next document provides a detailed hour-by-hour development timeline.*
