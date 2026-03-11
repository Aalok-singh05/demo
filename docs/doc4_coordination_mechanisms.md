# Document 4 — Coordination and Communication Mechanisms

---

## 4.1 The Orchestration Model: Why LangGraph's StateGraph

The coordination layer is the **most judged component** of this hackathon (25 points for "True multi-agent architecture, seamless autonomous handoffs, and shared memory"). Here's how we nail it.

### Why StateGraph over Sequential Chains

Most teams will do this:
```
User Input → Agent A → Agent B → Agent C → Output
```

This is a **pipeline**, not a multi-agent system. Judges will see through it.

Our system uses a **conditional state graph**:

```
                    ┌──────────────┐
                    │   ROUTER     │
                    │  (decides    │
                    │   next step) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Chronos  │ │  Hermes  │ │  Apollo  │
        │(Schedule)│ │  (Mail)  │ │(Content) │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          │
                    ┌─────▼──────┐
                    │  EVALUATOR │
                    │  (check if │
                    │  done or   │
                    │  route     │
                    │  again)    │
                    └─────┬──────┘
                          │
                   ┌──────┴──────┐
                   │             │
                   ▼             ▼
             ┌──────────┐  ┌─────────┐
             │  DONE    │  │ ROUTER  │ ← loops back!
             │  (return │  │ (more   │
             │  to user)│  │  work)  │
             └──────────┘  └─────────┘
```

The key difference: **the graph can loop**. After one agent finishes, the evaluator checks if cascading work is needed and routes back to another agent. This is how the Scheduler → Mailer handoff happens naturally.

---

## 4.2 LangGraph Implementation Design

### The State Object

This is the **single source of truth** shared by all agents:

```python
from typing import TypedDict, Annotated
from langgraph.graph import MessagesState

class NexusState(TypedDict):
    # User's original request
    user_input: str
    request_type: str  # "schedule", "mail", "content", "general", "multi"

    # Event data (shared across all agents)
    event_config: dict          # name, dates, venues, etc.
    participants: list[dict]    # clean participant data
    schedule: list[dict]        # current event schedule
    content_queue: list[dict]   # queued social/email content

    # Agent outputs (each agent writes here)
    scheduler_output: dict | None
    mailer_output: dict | None
    content_output: dict | None
    analytics_output: dict | None

    # Coordination state
    pending_tasks: list[dict]   # tasks that need another agent
    messages: list[dict]        # inter-agent messages
    activity_log: list[dict]    # for the frontend activity panel
    
    # Human-in-the-loop
    requires_approval: bool
    approval_items: list[dict]  # items waiting for organizer OK
    
    # Control flow
    next_agent: str | None
    iteration_count: int        # prevent infinite loops
```

### The Graph Definition

```python
from langgraph.graph import StateGraph, END

def build_nexus_graph():
    graph = StateGraph(NexusState)
    
    # Add nodes (agents)
    graph.add_node("router", route_request)
    graph.add_node("chronos", scheduler_agent)
    graph.add_node("hermes", mailer_agent)
    graph.add_node("apollo", content_agent)
    graph.add_node("athena", analytics_agent)
    graph.add_node("evaluator", evaluate_and_cascade)
    
    # Entry point
    graph.set_entry_point("router")
    
    # Router → Agent (conditional)
    graph.add_conditional_edges(
        "router",
        decide_agent,
        {
            "chronos": "chronos",
            "hermes": "hermes",
            "apollo": "apollo",
            "athena": "athena",
            "multi": "chronos",  # multi-agent starts with scheduler
        }
    )
    
    # Each agent → Evaluator
    for agent in ["chronos", "hermes", "apollo", "athena"]:
        graph.add_edge(agent, "evaluator")
    
    # Evaluator → Next step (conditional)
    graph.add_conditional_edges(
        "evaluator",
        decide_next_step,
        {
            "chronos": "chronos",
            "hermes": "hermes",
            "apollo": "apollo",
            "athena": "athena",
            "done": END,
            "approval_needed": END,  # pause for human approval
        }
    )
    
    return graph.compile()
```

### The Router Logic

```python
def decide_agent(state: NexusState) -> str:
    """Route based on request type and pending tasks."""
    
    # If there are pending cascading tasks, handle those first
    if state.get("pending_tasks"):
        next_task = state["pending_tasks"][0]
        return next_task["target_agent"]
    
    # Route based on user's request
    request_type = state.get("request_type", "general")
    
    routing_map = {
        "schedule": "chronos",
        "mail": "hermes",
        "content": "apollo",
        "analytics": "athena",
        "multi": "multi",
    }
    
    return routing_map.get(request_type, "chronos")
```

### The Evaluator (Cascading Logic)

This is the **most important function** — it's what makes the system truly multi-agent:

```python
def evaluate_and_cascade(state: NexusState) -> NexusState:
    """Check if the last agent's output requires another agent to act."""
    
    pending = list(state.get("pending_tasks", []))
    
    # Remove the task that was just completed
    if pending:
        pending.pop(0)
    
    # Check the last agent's output for cascading needs
    last_output = get_last_agent_output(state)
    
    if last_output and last_output.get("cascade_to"):
        for cascade in last_output["cascade_to"]:
            pending.append({
                "target_agent": cascade["agent"],
                "task": cascade["task"],
                "data": cascade["data"],
                "priority": cascade.get("priority", "normal"),
            })
    
    # Check if approval is needed
    if last_output and last_output.get("requires_approval"):
        return {
            **state,
            "pending_tasks": pending,
            "requires_approval": True,
            "approval_items": last_output["approval_items"],
        }
    
    # Safety: prevent infinite loops
    if state.get("iteration_count", 0) > 10:
        return {**state, "pending_tasks": [], "next_agent": None}
    
    return {
        **state,
        "pending_tasks": pending,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }

def decide_next_step(state: NexusState) -> str:
    """Determine the next node to execute."""
    if state.get("requires_approval"):
        return "approval_needed"
    
    if state.get("pending_tasks"):
        return state["pending_tasks"][0]["target_agent"]
    
    return "done"
```

---

## 4.3 Inter-Agent Communication Patterns

### Pattern 1: Direct Handoff (Scheduler → Mailer)

The most important pattern. When Chronos resolves a conflict:

```python
# Inside scheduler_agent function:
def scheduler_agent(state: NexusState) -> dict:
    # ... schedule conflict resolution logic ...
    
    affected = find_affected_participants(old_schedule, new_schedule)
    
    return {
        "scheduler_output": schedule_result,
        "schedule": new_schedule,
        "pending_tasks": [
            {
                "target_agent": "hermes",
                "task": "notify_schedule_change",
                "data": {
                    "affected_participants": affected,
                    "changes": schedule_diff,
                },
            },
            {
                "target_agent": "apollo",
                "task": "update_content",
                "data": {
                    "changed_sessions": changed_session_ids,
                },
            },
        ],
        "activity_log": state.get("activity_log", []) + [
            {
                "agent": "chronos",
                "action": "schedule_conflict_resolved",
                "details": f"Resolved {len(conflicts)} conflicts, {len(affected)} participants affected",
                "timestamp": datetime.now().isoformat(),
            }
        ],
    }
```

### Pattern 2: Broadcast (Analytics → Multiple Agents)

When Athena detects an issue, it broadcasts to relevant agents:

```python
# Athena detects low registration velocity
return {
    "analytics_output": analysis,
    "pending_tasks": [
        {
            "target_agent": "apollo",
            "task": "generate_urgency_content",
            "data": {"insight": "Registration 23% slower than expected"},
        },
        {
            "target_agent": "hermes",
            "task": "send_reminder",
            "data": {"segment": "registered_not_confirmed"},
        },
    ],
}
```

### Pattern 3: Request-Response (Meta-Agent → Specific Agents)

The Meta-Agent breaks down complex requests:

```python
# Organizer says: "Add a surprise keynote and tell everyone"
# Meta-agent decomposes into ordered tasks:
return {
    "pending_tasks": [
        {"target_agent": "chronos", "task": "add_session", "data": {...}, "priority": "critical"},
        # After chronos finishes, evaluator will check and route to hermes/apollo
    ],
}
```

---

## 4.4 Shared Memory Architecture

### Memory Layers

```
┌─────────────────────────────────────────┐
│         LAYER 1: Working Memory         │
│   (LangGraph State - current session)   │
│   • Current request context             │
│   • Agent outputs from this run         │
│   • Pending tasks                       │
│   Lives in: Python dict (memory)        │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         LAYER 2: Event Memory           │
│   (Persistent event data)              │
│   • Event configuration                │
│   • Participant registry               │
│   • Schedule timeline                  │
│   • Content queue                      │
│   Lives in: SQLite database             │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         LAYER 3: Agent Logs             │
│   (Historical activity)                │
│   • All agent actions + reasoning       │
│   • Inter-agent messages               │
│   • Organizer decisions (approved/      │
│     rejected/modified)                  │
│   Lives in: SQLite + in-memory cache    │
└─────────────────────────────────────────┘
```

### State Synchronization

All agents read from and write to the **same LangGraph state object**. LangGraph handles this natively:
- Each node receives the full state as input
- Each node returns a **partial state update** (only the fields it changed)
- LangGraph merges the partial update into the full state
- No race conditions because LangGraph executes nodes sequentially within a single invocation (parallelize only at the framework level)

---

## 4.5 Event-Driven Triggers

Beyond direct user commands, the system responds to **events**:

| Event | Trigger | Agents Activated |
|---|---|---|
| `PARTICIPANT_DATA_UPLOADED` | CSV uploaded via UI | Hermes (parse), Athena (analyze) |
| `SCHEDULE_CONSTRAINT_CHANGED` | Organizer edits a constraint | Chronos (rebuild), then cascade |
| `NEW_SESSION_ADDED` | Organizer adds a session | Chronos (fit into schedule) |
| `CONTENT_APPROVED` | Organizer approves content | Apollo (move to published queue) |
| `EMAIL_APPROVED` | Organizer approves email batch | Hermes (execute send) |
| `EVENT_DETAILS_CHANGED` | Any event metadata changes | Apollo (update content), Hermes (update templates) |
| `CAPACITY_WARNING` | Athena detects capacity issue | Chronos (suggest room swap) |

These events are processed through the **same LangGraph graph** — they enter at the router node and flow through the system naturally.

---

## 4.6 Human-in-the-Loop Mechanism

### The Approval Queue

Any consequential action (sending emails, publishing content, finalizing schedule) requires explicit organizer approval.

```python
class ApprovalItem(BaseModel):
    id: str
    agent: str              # which agent is requesting
    action: str             # what it wants to do
    description: str        # human-readable explanation
    preview: dict           # preview of the action (email content, schedule change, etc.)
    impact: str             # "Will affect 87 participants"
    options: list[str]      # ["approve", "edit", "reject"]
    created_at: datetime
```

### Frontend Approval Flow

```
┌──────────────────────────────────────────────┐
│  📋 Pending Approvals (3)                    │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 📧 Hermes wants to send emails         │  │
│  │ "Schedule update notification"         │  │
│  │ To: 87 affected participants           │  │
│  │                                        │  │
│  │ Preview: "Dear {{name}}, the workshop  │  │
│  │ you registered for has moved to..."    │  │
│  │                                        │  │
│  │ [✅ Approve] [✏️ Edit] [❌ Reject]     │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 📱 Apollo wants to update a post       │  │
│  │ "Correction: Keynote now at 2:00 PM"   │  │
│  │                                        │  │
│  │ [✅ Approve] [✏️ Edit] [❌ Reject]     │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

When the organizer approves, the system:
1. Updates the approval status in state
2. Re-enters the graph to execute the approved action
3. Logs the decision for future reference

---

## 4.7 WebSocket Streaming Protocol

Real-time communication between backend and frontend:

```python
# Backend sends these message types via WebSocket:

class WSMessage(BaseModel):
    type: str  # "agent_activity", "approval_request", "state_update", "error"
    data: dict
    timestamp: datetime

# Examples:
# Agent starts working:
{"type": "agent_activity", "data": {"agent": "chronos", "status": "working", "task": "Resolving schedule conflict..."}}

# Agent completes:
{"type": "agent_activity", "data": {"agent": "chronos", "status": "done", "result": "3 conflicts resolved"}}

# Inter-agent message:
{"type": "agent_message", "data": {"from": "chronos", "to": "hermes", "message": "87 participants affected by schedule change"}}

# Approval needed:
{"type": "approval_request", "data": {"items": [...]}}

# State update:
{"type": "state_update", "data": {"field": "schedule", "action": "updated"}}
```

Frontend listens on a WebSocket connection and updates the UI reactively as messages arrive. This creates the "living dashboard" effect that will impress judges.

---

*The next document explores creative features and innovations that push the system beyond the baseline requirements.*
