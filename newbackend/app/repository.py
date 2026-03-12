# Database CRUD repository

import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.database import get_db


# --- Events ---

async def create_event(event_data: dict) -> dict:
    db = await get_db()
    event_id = event_data.get("id", str(uuid.uuid4()))
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO events (id, name, description, start_date, end_date,
           location, organizer_name, status, config_json, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (event_id, event_data.get("name", ""), event_data.get("description"),
         event_data.get("start_date"), event_data.get("end_date"),
         event_data.get("location"), event_data.get("organizer_name"),
         event_data.get("status", "draft"), json.dumps(event_data.get("config", {})),
         now, now)
    )
    await db.commit()
    event_data["id"] = event_id
    event_data["created_at"] = now
    event_data["updated_at"] = now
    return event_data


async def get_event_by_id(event_id: str) -> Optional[dict]:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_all_events() -> List[dict]:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM events ORDER BY created_at DESC")
    return [dict(row) for row in await cursor.fetchall()]


# --- Participants ---

async def insert_participants(event_id: str, participants: List[dict]) -> int:
    db = await get_db()
    now = datetime.now().isoformat()
    count = 0
    for p in participants:
        pid = str(uuid.uuid4())
        await db.execute(
            """INSERT INTO participants (id, event_id, name, email, role, track,
               organization, phone, is_valid_email, metadata_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (pid, event_id, p.get("name", ""), p.get("email", ""),
             p.get("role", "attendee"), p.get("track", ""),
             p.get("organization", ""), p.get("phone", ""),
             1 if p.get("is_valid_email", True) else 0,
             json.dumps(p.get("metadata", {})), now)
        )
        count += 1
    await db.commit()
    return count


async def get_participants(event_id: str) -> List[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM participants WHERE event_id = ? ORDER BY created_at", (event_id,))
    return [dict(row) for row in await cursor.fetchall()]


# --- Sessions ---

async def insert_session(event_id: str, session_data: dict) -> dict:
    db = await get_db()
    sid = session_data.get("id", str(uuid.uuid4()))
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO sessions (id, event_id, title, description, session_type,
           speaker, venue, start_time, end_time, day, capacity, is_fixed,
           status, metadata_json, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, event_id, session_data.get("title", ""),
         session_data.get("description"), session_data.get("session_type", "talk"),
         session_data.get("speaker"), session_data.get("venue"),
         session_data.get("start_time"), session_data.get("end_time"),
         session_data.get("day"), session_data.get("capacity"),
         1 if session_data.get("is_fixed") else 0,
         session_data.get("status", "scheduled"),
         json.dumps(session_data.get("metadata", {})), now, now)
    )
    await db.commit()
    session_data["id"] = sid
    return session_data


async def get_sessions(event_id: str) -> List[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM sessions WHERE event_id = ? ORDER BY day, start_time", (event_id,))
    return [dict(row) for row in await cursor.fetchall()]


# --- Content Queue ---

async def insert_content(event_id: str, content_data: dict) -> dict:
    db = await get_db()
    cid = content_data.get("id", str(uuid.uuid4()))
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO content_queue (id, event_id, content_type, platform, title,
           body, tone, hashtags, scheduled_time, status, agent_reasoning,
           created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cid, event_id, content_data.get("content_type", "social_post"),
         content_data.get("platform"), content_data.get("title"),
         content_data.get("body", ""), content_data.get("tone"),
         content_data.get("hashtags", ""), content_data.get("scheduled_time"),
         content_data.get("status", "draft"), content_data.get("reasoning"),
         now, now)
    )
    await db.commit()
    content_data["id"] = cid
    return content_data


# --- Approvals ---

async def insert_approval(event_id: str, approval_data: dict) -> dict:
    db = await get_db()
    aid = approval_data.get("id", str(uuid.uuid4()))
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO approvals (id, event_id, agent, action, description,
           impact, preview_json, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (aid, event_id, approval_data.get("agent", ""),
         approval_data.get("action", ""), approval_data.get("description", ""),
         approval_data.get("impact", ""), json.dumps(approval_data.get("preview", {})),
         "pending", now)
    )
    await db.commit()
    approval_data["id"] = aid
    return approval_data


# --- Agent Logs ---

async def insert_agent_log(log_data: dict) -> str:
    db = await get_db()
    log_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO agent_logs (id, event_id, agent, action, details,
           reasoning, from_agent, to_agent, trace_id, log_level, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (log_id, log_data.get("event_id"), log_data.get("agent", "system"),
         log_data.get("action", ""), log_data.get("details"),
         log_data.get("reasoning"), log_data.get("from_agent"),
         log_data.get("to_agent"), log_data.get("trace_id"),
         log_data.get("log_level", "info"), now)
    )
    await db.commit()
    return log_id


async def get_agent_logs(event_id: Optional[str] = None, limit: int = 50) -> List[dict]:
    db = await get_db()
    query = "SELECT * FROM agent_logs"
    params = []
    if event_id:
        query += " WHERE event_id = ?"
        params.append(event_id)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cursor = await db.execute(query, tuple(params))
    return [dict(row) for row in await cursor.fetchall()]
