"""Dashboard, Activity Feed, Approvals, and Insights API routes."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import json

from ...database import get_db
from ...models.schemas import (
    EventOverview, ActivityItem, Approval, ApprovalAction, Insight
)
from ...api.websocket import manager

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=EventOverview)
async def get_dashboard():
    """Get event overview / dashboard metrics."""
    db = await get_db()
    try:
        row = await db.execute_fetchall("SELECT * FROM events LIMIT 1")
        if not row:
            return EventOverview(
                name="No Event", venue="N/A", days=0,
                attendees=0, sessions=0, speakers=0, status="inactive"
            )
        e = row[0]
        return EventOverview(
            name=e[1], venue=e[2], days=e[3],
            attendees=e[4], sessions=e[5], speakers=e[6], status=e[7]
        )
    finally:
        await db.close()


@router.get("/activity", response_model=list[ActivityItem])
async def get_activity():
    """Get activity feed items."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, time, agent, text, status, details FROM activity_log ORDER BY id DESC LIMIT 50"
        )
        return [
            ActivityItem(id=r[0], time=r[1], agent=r[2], text=r[3], status=r[4], details=r[5])
            for r in rows
        ]
    finally:
        await db.close()


@router.get("/approvals", response_model=list[Approval])
async def get_approvals():
    """Get pending approval items."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, title, agent, desc, impact, preview, status FROM approvals WHERE status = 'pending' ORDER BY id DESC"
        )
        return [
            Approval(id=r[0], title=r[1], agent=r[2], desc=r[3], impact=r[4], preview=r[5], status=r[6])
            for r in rows
        ]
    finally:
        await db.close()


@router.post("/approvals/{approval_id}/action")
async def handle_approval(approval_id: int, body: ApprovalAction):
    """Approve, reject, or edit an approval."""
    db = await get_db()
    try:
        # Check if exists
        row = await db.execute_fetchall(
            "SELECT id, title, agent FROM approvals WHERE id = ?", (approval_id,)
        )
        if not row:
            raise HTTPException(status_code=404, detail="Approval not found")

        new_status = body.action  # "approve" | "reject" | "edit"
        await db.execute(
            "UPDATE approvals SET status = ? WHERE id = ?",
            (new_status, approval_id)
        )
        await db.commit()

        # Log activity
        action_text = f"{row[0][2]} task '{row[0][1]}' was {new_status}d by Organizer."
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "System", action_text, "done")
        )
        await db.commit()

        # Broadcast
        await manager.broadcast("approval_action", {
            "approval_id": approval_id,
            "action": body.action,
            "message": action_text
        })

        return {"status": "ok", "action": body.action}
    finally:
        await db.close()


@router.get("/insights", response_model=list[Insight])
async def get_insights():
    """Get analytics insights from Athena."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, type, title, desc, action FROM insights ORDER BY id DESC"
        )
        return [
            Insight(id=r[0], type=r[1], title=r[2], desc=r[3], action=r[4])
            for r in rows
        ]
    finally:
        await db.close()
