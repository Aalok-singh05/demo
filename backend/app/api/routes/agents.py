"""Agent system API routes — state, logs, status, budget, and chat."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json

from ...database import get_db
from ...models.schemas import (
    AgentStatus, AgentState, AgentLogEntry, PendingTask,
    BudgetSummary, BudgetItem, ChatRequest, ChatResponse
)
from ...api.websocket import manager
from ...agents.meta_agent import handle_chat_message
from ...agents.budget import get_budget_analysis

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/status", response_model=list[AgentStatus])
async def get_agent_statuses():
    """Get current status of all agents."""
    # In a real system this would track actual agent state.
    # Reads latest activity to infer status.
    db = await get_db()
    try:
        agents_conf = [
            {"name": "Chronos", "role": "Scheduler"},
            {"name": "Hermes", "role": "Mailer"},
            {"name": "Apollo", "role": "Content"},
            {"name": "Athena", "role": "Analytics"},
            {"name": "Nexus Core", "role": "Meta-Coordinator"},
            {"name": "Fortuna", "role": "Budget Tracker"},
        ]
        result = []
        for agent in agents_conf:
            row = await db.execute_fetchall(
                "SELECT text, status FROM activity_log WHERE agent = ? ORDER BY id DESC LIMIT 1",
                (agent["name"],)
            )
            if row:
                latest_status = row[0][1]
                current_task = row[0][0][:60] + "..." if len(row[0][0]) > 60 else row[0][0]
            else:
                latest_status = "idle"
                current_task = ""

            status_map = {
                "working": "working",
                "done": "idle",
                "pending": "observing",
            }
            result.append(AgentStatus(
                name=agent["name"],
                role=agent["role"],
                status=status_map.get(latest_status, "idle"),
                current_task=current_task
            ))
        return result
    finally:
        await db.close()


@router.get("/state", response_model=AgentState)
async def get_agent_state():
    """Get current LangGraph state."""
    db = await get_db()
    try:
        row = await db.execute_fetchall("SELECT state_json FROM agent_state WHERE id = 1")
        if row:
            state = json.loads(row[0][0])
            return AgentState(
                iteration_count=state.get("iteration_count", 0),
                next_agent=state.get("next_agent", "none"),
                requires_approval=state.get("requires_approval", False),
                pending_tasks=[
                    PendingTask(**t) for t in state.get("pending_tasks", [])
                ],
                event_config=state.get("event_config", {}),
                conflicts_resolved=state.get("conflicts_resolved", 0),
                latest_trigger=state.get("latest_trigger", "NONE")
            )
        # Fallback
        return AgentState(
            iteration_count=0, next_agent="none",
            requires_approval=False, pending_tasks=[],
            event_config={}, conflicts_resolved=0,
            latest_trigger="NONE"
        )
    finally:
        await db.close()


@router.get("/logs", response_model=list[AgentLogEntry])
async def get_agent_logs():
    """Get reasoning chain / agent log entries."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, timestamp, agent, action, reasoning, cascaded_to, status FROM agent_logs ORDER BY id"
        )
        return [
            AgentLogEntry(
                id=r[0], timestamp=r[1], agent=r[2], action=r[3],
                reasoning=r[4], cascaded_to=json.loads(r[5]) if r[5] else [],
                status=r[6]
            )
            for r in rows
        ]
    finally:
        await db.close()


# ── Budget (Fortuna) ──────────────────────────────────────

@router.get("/budget", response_model=BudgetSummary)
async def get_budget():
    """Get budget summary from Fortuna agent."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, category, description, amount, type FROM budget_items ORDER BY type, category"
        )
        items = [
            BudgetItem(id=r[0], category=r[1], description=r[2], amount=r[3], type=r[4])
            for r in rows
        ]

        result = await get_budget_analysis(items)
        return result
    finally:
        await db.close()


# ── Chat (Nexus Core / Meta-Agent) ────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """Send a message to the Meta-Agent (Nexus Core)."""
    result = await handle_chat_message(body.message)

    # Store in chat history
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
            ("user", body.message, datetime.now().isoformat())
        )
        await db.execute(
            "INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
            ("assistant", result.reply, datetime.now().isoformat())
        )

        # Log activity
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Nexus Core",
             f"Processed organizer request: \"{body.message[:80]}...\"" if len(body.message) > 80 else f"Processed organizer request: \"{body.message}\"",
             "done")
        )

        # Agent log
        plan_text = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(result.plan))
        await db.execute(
            "INSERT INTO agent_logs (timestamp, agent, action, reasoning, cascaded_to) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Nexus Core",
             "Workflow Planning",
             f"User request: \"{body.message}\"\n\nPlan:\n{plan_text}\n\nResponse: {result.reply}",
             json.dumps(result.agents_involved))
        )
        await db.commit()

        await manager.broadcast("agent_activity", {
            "agent": "Nexus Core",
            "action": "Chat Response",
            "text": f"Nexus Core responded to organizer request.",
            "status": "done"
        })
    finally:
        await db.close()

    return result
