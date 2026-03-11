"""Mail Center API routes — CSV upload, participant management, email personalization."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
import json
import io

from ...database import get_db
from ...models.schemas import (
    Participant, UploadResult, EmailTemplate, PersonalizeResult,
    EmailPreview, SendResult
)
from ...api.websocket import manager
from ...agents.mailer import parse_and_validate_csv, personalize_emails

router = APIRouter(prefix="/api/mail", tags=["mail"])


@router.get("/participants", response_model=list[Participant])
async def get_participants():
    """Get validated participant list."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, name, email, role, status FROM participants ORDER BY status DESC, id"
        )
        return [
            Participant(id=r[0], name=r[1], email=r[2], role=r[3], status=r[4])
            for r in rows
        ]
    finally:
        await db.close()


@router.post("/upload", response_model=UploadResult)
async def upload_participants(file: UploadFile = File(...)):
    """Upload CSV/Excel file — Hermes parses and validates."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files accepted")

    content = await file.read()

    # Run Hermes agent
    result = await parse_and_validate_csv(content, ext, file.filename)

    # Store valid participants in DB
    db = await get_db()
    try:
        for p in result.participants:
            await db.execute(
                "INSERT OR IGNORE INTO participants (name, email, role, status) VALUES (?, ?, ?, ?)",
                (p.name, p.email, p.role, p.status)
            )

        # Update event attendee count
        count_row = await db.execute_fetchall("SELECT COUNT(*) FROM participants WHERE status = 'valid'")
        count = count_row[0][0]
        await db.execute("UPDATE events SET attendees = ?", (count,))

        # Log activity
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status, details) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Hermes",
             f"Processed {result.total_parsed} participants from {file.filename}. "
             f"{result.invalid_emails} invalid emails flagged.",
             "done", f"Valid: {result.valid_emails}, Invalid: {result.invalid_emails}, Duplicates: {result.duplicates}")
        )
        await db.commit()

        # Broadcast
        await manager.broadcast("agent_activity", {
            "agent": "Hermes",
            "action": "CSV Processing",
            "text": f"Processed {result.total_parsed} participants. {result.invalid_emails} invalid.",
            "status": "done"
        })
    finally:
        await db.close()

    return result


@router.post("/personalize", response_model=PersonalizeResult)
async def personalize(body: EmailTemplate):
    """Generate email previews from template + participant data."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, name, email, role FROM participants WHERE status = 'valid' LIMIT 5"
        )
        participants = [
            {"name": r[1], "email": r[2], "role": r[3]}
            for r in rows
        ]

        result = await personalize_emails(body.template, participants)
        return result
    finally:
        await db.close()


@router.post("/send", response_model=SendResult)
async def send_batch():
    """Queue batch email send (simulated)."""
    db = await get_db()
    try:
        count_row = await db.execute_fetchall(
            "SELECT COUNT(*) FROM participants WHERE status = 'valid'"
        )
        count = count_row[0][0]

        # Log activity
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Hermes",
             f"Queued {count} personalized emails for distribution.", "done")
        )
        await db.commit()

        await manager.broadcast("agent_activity", {
            "agent": "Hermes",
            "action": "Email Batch",
            "text": f"Queued {count} emails for distribution.",
            "status": "done"
        })

        return SendResult(queued=count, status="queued")
    finally:
        await db.close()
