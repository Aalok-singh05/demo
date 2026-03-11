# Document 8 — Development Roadmap

---

## 8.1 Timeline Assumptions

- **Total hackathon time:** ~12 hours of focused development
- **Team size:** 4 (3 on-site, 1 remote)
- **Buffer:** Last 1–2 hours reserved for demo preparation and polish
- **Milestones are designed as "runnable demos"** — at every milestone checkpoint, you should have a demoable system, even if incomplete

---

## 8.2 Hour-by-Hour Development Plan

---

### ⏰ HOUR 0–1: Project Setup & Contract Agreement

**Goal:** Everyone can start coding independently within 60 minutes.

| Who | Task | Deliverable |
|---|---|---|
| **You** | Create project skeleton (backend/, frontend/ folders), write all Pydantic models, set up `requirements.txt` | Shared project structure on Git |
| **Member 2** | Set up their local dev environment, pull repo, review agent schemas | Ready to code |
| **Member 3** | Initialize FastAPI app, set up SQLite, create boilerplate routes | Running backend on `localhost:8000` |
| **Member 4** | Initialize React + Vite app, install UI library, set up routing shell | Running frontend on `localhost:5173` |
| **All (30 min)** | **API Contract Meeting**: Agree on all endpoint shapes, WebSocket format, agent response schemas | Shared API spec document |

**Milestone 0:** Both frontend and backend servers are running. Git repo has clean structure. Everyone understands their role.

---

### ⏰ HOURS 1–3: Foundation Sprint

**Goal:** A working end-to-end pipeline with mock AI.

| Who | Task |
|---|---|
| **You** | Build LangGraph StateGraph skeleton with mock agents. Each agent returns dummy structured data. Build the WebSocket streaming mechanism. |
| **Member 2** | Build CSV parser, email validator, participant segmenter as standalone Python modules. Create test data files. |
| **Member 3** | Build all REST endpoints: event CRUD, file upload, `/agents/invoke`, `/ws/stream`. Connect to SQLite for persistence. |
| **Member 4** | Build Dashboard layout with: event overview card, agent status sidebar, activity feed (mock data), and the approval card component. |

**Milestone 1 (End of Hour 3):** 
- Frontend Dashboard shows mock event data
- An API call to `/agents/invoke` triggers the LangGraph graph, which returns mock agent output
- WebSocket connection streams activity from backend to frontend
- **First Integration Test:** Frontend → API → LangGraph → Mock Agent → WebSocket → Frontend Activity Feed

> **This is the most critical milestone.** If data flows end-to-end, everything else is incremental. If it doesn't, stop and fix it before moving on.

---

### ⏰ HOURS 3–6: Core Agent Development Sprint

**Goal:** All three baseline agents are functional with real LLM intelligence.

| Who | Task |
|---|---|
| **You** | Implement **Chronos** (Scheduler Agent) with LLM integration. Build constraint-based scheduling, conflict detection, and cascading notification triggers. Then implement **Hermes** (Mail Agent): CSV processing, email personalization, segment-based distribution. |
| **Member 2** | Implement **Apollo** (Content Agent): content generation, campaign planning, platform-specific output. Start on system prompt optimization for all agents. Build engagement analysis tool. |
| **Member 3** | Integrate real agent outputs into API→WebSocket pipeline. Build the approval workflow backend (store pending, handle approve/reject). Implement file upload for CSV processing. |
| **Member 4** | Build **Schedule View** page (interactive timeline grid). Build **Mail Center** page (CSV upload + data preview + email preview). Start **Content Studio** page. |

**Integration Checkpoint (Hour 4):** You + Member 3 connect real LangGraph agent outputs to the API. Frontend should now show real agent activity.

**Milestone 2 (End of Hour 6):**
- Chronos can generate a schedule from constraints and detect/resolve conflicts
- Hermes can parse a CSV and generate personalized email previews
- Apollo can generate promotional content in multiple tones
- **The cascading demo works:** change a schedule constraint → Chronos resolves → triggers Hermes notification → activity feed shows the chain
- All three core pages (Schedule, Mail, Content) are functional in the frontend

> **This is the "baseline complete" milestone.** At this point, you can score full marks on Core Implementation (25) and Baseline Functionality (25). Everything after this is bonus points.

---

### ⏰ HOURS 6–8: Innovation Sprint

**Goal:** Add distinctive features that differentiate from other teams.

| Who | Task |
|---|---|
| **You** | Implement **Athena** (Analytics Agent) with insights. Build the What-If Simulator. Add reasoning chain output to all agents. |
| **Member 2** | Build the natural language command router (Meta-Agent logic). Create the demo dataset (realistic event with carefully designed conflicts). Test all agent interactions. |
| **Member 3** | Implement the simulation endpoint (`/schedule/simulate`). Add the activity log persistence. Optimize error handling and agent recovery. |
| **Member 4** | Build the **Agent Activity detail view** with reasoning chain visualization. Add agent working animations. Build the command bar at the top. |

**Milestone 3 (End of Hour 8):**
- Athena provides real-time insights on the dashboard
- What-If simulator works: organizer sees impact before committing
- Reasoning chains are visible in the UI
- Natural language command bar routes requests to the right agents
- **Innovation demo works:** organizer asks a question in natural language → system decomposes into multi-agent tasks → visible chain of reasoning

---

### ⏰ HOURS 8–10: Polish Sprint

**Goal:** Make everything look and feel production-grade.

| Who | Task |
|---|---|
| **You** | Fine-tune agent prompts for quality. Edge case handling. Prepare demo flow data. |
| **Member 2** | Write the demo script (exact steps, exact data to use). Test edge cases. Fix any AI-side bugs. |
| **Member 3** | Backend stability: handle WebSocket reconnections, API error responses, logging. |
| **Member 4** | Visual polish: animations, color refinement, loading states, error states. Make the "judge walk-through" path seamless. |

**Milestone 4 (End of Hour 10):**
- System is stable — no crashes during the demo flow
- Visual design is professional and polished
- Demo data is prepared and tested
- A few innovation features are clearly visible

---

### ⏰ HOURS 10–12: Demo Preparation & Rehearsal

**Goal:** Deliver a flawless presentation.

| Who | Task |
|---|---|
| **All** | Run through the full demo 2-3 times. Fix any issues discovered. |
| **You** | Prepare to explain the architecture and multi-agent design to judges. |
| **Member 2** | Prepare backup demo data in case primary data has issues. |
| **Member 3** | Pre-seed the database with demo data so the system starts in a rich state. |
| **Member 4** | Final UI adjustments based on demo rehearsal. Screenshots for backup slides. |

**Milestone 5 (Demo Time):**
- Team has rehearsed the demo 2+ times
- Everyone knows their speaking parts
- Backup plans are in place (pre-computed results, screenshots, backup data)

---

## 8.3 The "If Everything Goes Wrong" Plan

If you're behind schedule at any checkpoint, here's what to cut:

### Hour 3: If end-to-end pipeline isn't working
- **Cut:** Skip WebSocket streaming temporarily. Use REST polling instead.
- **Focus:** Get the LangGraph → API → Frontend data flow working.

### Hour 6: If baseline agents aren't all working
- **Cut:** Simplify the weakest agent to use hardcoded templates instead of LLM.
- **Focus:** Make the cascading demo work perfectly with at least 2 real agents.

### Hour 8: If innovation features aren't ready
- **Cut:** Skip What-If simulator and natural language command bar.
- **Focus:** Polish the reasoning chain visualization (it's tied to judging criteria).

### Hour 10: If UI isn't polished
- **Cut:** Use component library defaults. No custom animations.
- **Focus:** Make the demo flow work flawlessly. Substance over style.

### Nuclear Option: Pre-Computed Demo
If the system is unstable:
- Pre-compute all agent responses
- Hardcode them into the frontend
- Demo looks perfect but isn't live
- **Only use this as an absolute last resort** — judges may ask to interact with the system

---

## 8.4 Git Strategy

```
main ─── stable, always demoable
  ├── dev ─── integration branch
  │    ├── ai/scheduler-agent
  │    ├── ai/mailer-agent
  │    ├── ai/content-agent
  │    ├── backend/api-routes
  │    ├── backend/websocket
  │    ├── frontend/dashboard
  │    ├── frontend/schedule-view
  │    └── frontend/mail-center
```

- Merge to `dev` frequently (every 1–2 hours)
- Merge `dev` to `main` only when verified working
- Before demo: demo from `main`

---

## 8.5 Development Environment

| Tool | Purpose |
|---|---|
| VS Code | Primary IDE for all members |
| Python 3.11+ | Backend runtime |
| Node.js 18+ | Frontend runtime |
| GitHub | Version control + collaboration |
| `.env` file | API keys (never committed) |
| SQLite | Database (zero setup) |
| Postman / Thunder Client | API testing |
| Browser DevTools | WebSocket debugging |

---

*The final document covers how to present all of this to the judges.*
