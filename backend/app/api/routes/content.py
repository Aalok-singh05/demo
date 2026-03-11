"""Content Studio API routes — content generation and queue management."""
from fastapi import APIRouter
from datetime import datetime
import json

from ...database import get_db
from ...models.schemas import ContentRequest, ContentPiece, GenerateResult, ContentQueueItem
from ...api.websocket import manager
from ...agents.content import generate_content

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/generate", response_model=GenerateResult)
async def generate(body: ContentRequest):
    """Trigger Apollo agent to generate content variants."""
    result = await generate_content(body.brief, body.platforms, body.tone)

    # Store in DB
    db = await get_db()
    try:
        for variant in result.variants:
            await db.execute(
                "INSERT INTO content_queue (platform, tone, text, image_prompt, status, is_recommended) VALUES (?, ?, ?, ?, ?, ?)",
                (variant.platform, variant.tone, variant.text,
                 variant.image_prompt, "draft", 1 if variant.is_recommended else 0)
            )

        # Log activity
        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status, details) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Apollo",
             f"Generated {len(result.variants)} content variants for {', '.join(body.platforms)}.",
             "done", result.reasoning)
        )

        # Agent reasoning log
        await db.execute(
            "INSERT INTO agent_logs (timestamp, agent, action, reasoning, cascaded_to) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "Apollo",
             "Content Generation", result.reasoning, "[]")
        )
        await db.commit()

        await manager.broadcast("agent_activity", {
            "agent": "Apollo",
            "action": "Content Generation",
            "text": f"Generated {len(result.variants)} content variants.",
            "status": "done"
        })
    finally:
        await db.close()

    return result


@router.get("/queue", response_model=list[ContentPiece])
async def get_queue():
    """Get content queue with all items."""
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT id, platform, tone, text, image_prompt, scheduled_time, status, is_recommended FROM content_queue ORDER BY id DESC"
        )
        return [
            ContentPiece(
                id=r[0], platform=r[1], tone=r[2], text=r[3],
                image_prompt=r[4], scheduled_time=r[5],
                status=r[6], is_recommended=bool(r[7])
            )
            for r in rows
        ]
    finally:
        await db.close()


@router.post("/queue/{item_id}/approve")
async def approve_content(item_id: int):
    """Approve a content piece for publishing."""
    db = await get_db()
    try:
        row = await db.execute_fetchall("SELECT id, platform FROM content_queue WHERE id = ?", (item_id,))
        if not row:
            return {"status": "error", "detail": "Content not found"}

        await db.execute("UPDATE content_queue SET status = 'approved' WHERE id = ?", (item_id,))

        await db.execute(
            "INSERT INTO activity_log (time, agent, text, status) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%I:%M %p"), "System",
             f"Content #{item_id} ({row[0][1]}) approved and queued for publishing.", "done")
        )
        await db.commit()

        await manager.broadcast("content_approved", {"id": item_id, "platform": row[0][1]})

        return {"status": "ok", "item_id": item_id}
    finally:
        await db.close()
