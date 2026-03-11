"""Schedule management API routes."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import json

from ...database import get_db
from ...models.schemas import Session, SessionCreate, ScheduleOptimizeResult, ConflictInfo
from ...api.websocket import manager
from ...agents.scheduler import optimize_schedule

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("/sessions", response_model=list[Session])
async def get_sessions():
    """Get all scheduled sessions."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, title, time, room, speaker, type, has_conflict, conflict_with FROM sessions ORDER BY day, id"
        )
        return [
            Session(
                id=r[0], title=r[1], time=r[2], room=r[3],
                speaker=r[4], type=r[5],
                has_conflict=bool(r[6]), conflict_with=r[7]
            )
            for r in rows
        ]
    finally:
        await db.close()


@router.post("/sessions", response_model=Session)
async def create_session(body: SessionCreate):
    """Add a new session to the schedule."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO sessions (title, time, room, speaker, type) VALUES (?, ?, ?, ?, ?)",
            (body.title, body.time, body.room, body.speaker, body.type)
        )
        await db.commit()
        new_id = cursor.lastrowid

        # Log activity
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "System",
             f"New session added: \"{body.title}\" at {body.time} in {body.room}", "done")
        )
        await db.commit()

        # Broadcast
        await manager.broadcast("session_added", {
            "id": new_id, "title": body.title, "time": body.time, "room": body.room
        })

        return Session(
            id=new_id, title=body.title, time=body.time,
            room=body.room, speaker=body.speaker, type=body.type
        )
    finally:
        await db.close()


@router.put("/sessions/{session_id}")
async def update_session(session_id: int, body: SessionCreate):
    """Update a session's time or room."""
    db = await get_db()
    try:
        row = await db.execute_fetchall("SELECT id FROM sessions WHERE id = ?", (session_id,))
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")

        await db.execute(
            "UPDATE sessions SET title = ?, time = ?, room = ?, speaker = ?, type = ? WHERE id = ?",
            (body.title, body.time, body.room, body.speaker, body.type, session_id)
        )
        await db.commit()

        # Log
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "System",
             f"Session \"{body.title}\" updated to {body.time} in {body.room}", "done")
        )
        await db.commit()

        await manager.broadcast("session_updated", {"id": session_id, "title": body.title})

        return {"status": "ok", "session_id": session_id}
    finally:
        await db.close()


@router.post("/optimize", response_model=ScheduleOptimizeResult)
async def run_optimize():
    """Trigger Chronos agent to detect and resolve schedule conflicts."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, title, time, room, speaker, type, has_conflict, conflict_with FROM sessions ORDER BY day, id"
        )
        sessions = [
            {"id": r[0], "title": r[1], "time": r[2], "room": r[3],
             "speaker": r[4], "type": r[5], "has_conflict": bool(r[6]),
             "conflict_with": r[7]}
            for r in rows
        ]

        # Run Chronos agent
        result = await optimize_schedule(sessions)

        # Log the agent activity
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status, details) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Chronos",
             f"Schedule optimization complete. {result.conflicts_resolved} conflicts resolved.",
             "done", result.reasoning)
        )

        # Log to agent reasoning chain
        await db.execute(
            "INSERT INTO agent_logs (timestamp, agent, action, reasoning, cascaded_to) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Chronos", "Schedule Optimization",
             result.reasoning, json.dumps(["hermes", "apollo"]))
        )
        await db.commit()

        # Broadcast real-time update
        await manager.broadcast("agent_activity", {
            "agent": "Chronos",
            "action": "Schedule Optimization",
            "text": f"Resolved {result.conflicts_resolved} conflicts.",
            "status": "done"
        })

        return result
    finally:
        await db.close()
