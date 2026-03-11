"""Pydantic schemas for all API request/response models."""
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ── Dashboard ──────────────────────────────────────────────
class EventOverview(BaseModel):
    name: str
    venue: str
    days: int
    attendees: int
    sessions: int
    speakers: int
    status: str = "active"


class ActivityItem(BaseModel):
    id: int
    time: str
    agent: str
    text: str
    status: str = "done"
    details: str | None = None


class Approval(BaseModel):
    id: int
    title: str
    agent: str
    desc: str
    impact: str
    preview: str
    status: str = "pending"


class ApprovalAction(BaseModel):
    action: str  # "approve", "reject", "edit"


class Insight(BaseModel):
    id: int
    type: str  # "warning", "info", "success"
    title: str
    desc: str
    action: str = ""


# ── Schedule ───────────────────────────────────────────────
class Session(BaseModel):
    id: int
    title: str
    time: str
    room: str
    speaker: str
    type: str  # "keynote", "workshop", "panel", "break"
    has_conflict: bool = False
    conflict_with: int | None = None


class SessionCreate(BaseModel):
    title: str
    time: str
    room: str
    speaker: str = ""
    type: str = "workshop"


class ConflictInfo(BaseModel):
    session_a_id: int
    session_b_id: int
    room: str
    time_overlap: str
    description: str


class ScheduleOptimizeResult(BaseModel):
    conflicts_found: list[ConflictInfo]
    conflicts_resolved: int
    changes_made: list[str]
    reasoning: str


# ── Mail Center ────────────────────────────────────────────
class Participant(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str = "valid"  # "valid", "invalid"


class UploadResult(BaseModel):
    total_parsed: int
    valid_emails: int
    invalid_emails: int
    duplicates: int
    participants: list[Participant]


class EmailTemplate(BaseModel):
    template: str
    segment_criteria: str = "all"


class EmailPreview(BaseModel):
    recipient_name: str
    recipient_email: str
    subject: str
    body: str


class PersonalizeResult(BaseModel):
    previews: list[EmailPreview]
    total_recipients: int


class SendResult(BaseModel):
    queued: int
    status: str


# ── Content Studio ─────────────────────────────────────────
class ContentRequest(BaseModel):
    brief: str
    platforms: list[str] = ["linkedin", "twitter"]
    tone: str = "professional"


class ContentPiece(BaseModel):
    id: int
    platform: str
    tone: str
    text: str
    image_prompt: str = ""
    scheduled_time: str = ""
    status: str = "draft"  # "draft", "approved", "published"
    is_recommended: bool = False


class ContentQueueItem(BaseModel):
    id: int
    label: str
    time: str
    type: str  # "teaser", "speaker_bio", "live_update"


class GenerateResult(BaseModel):
    variants: list[ContentPiece]
    campaign_timeline: list[ContentQueueItem]
    reasoning: str


# ── Agent System ───────────────────────────────────────────
class AgentStatus(BaseModel):
    name: str
    role: str
    status: str  # "idle", "working", "observing", "planning"
    current_task: str = ""


class PendingTask(BaseModel):
    target: str
    task: str
    status: str


class AgentState(BaseModel):
    iteration_count: int
    next_agent: str
    requires_approval: bool
    pending_tasks: list[PendingTask]
    event_config: dict
    conflicts_resolved: int
    latest_trigger: str


class AgentLogEntry(BaseModel):
    id: int
    timestamp: str
    agent: str
    action: str
    reasoning: str
    cascaded_to: list[str] = []
    status: str = "completed"


# ── Budget (Fortuna) ──────────────────────────────────────
class BudgetItem(BaseModel):
    id: int
    category: str
    description: str
    amount: float
    type: str  # "expense", "revenue"


class BudgetSummary(BaseModel):
    total_revenue: float
    total_expenses: float
    net_balance: float
    items: list[BudgetItem]
    warnings: list[str]


# ── Meta Agent (Nexus Core) Chat ──────────────────────────
class ChatMessage(BaseModel):
    role: str  # "user", "assistant"
    content: str
    timestamp: str = ""


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    plan: list[str] = []
    agents_involved: list[str] = []


# ── WebSocket Events ──────────────────────────────────────
class WSEvent(BaseModel):
    type: str  # "activity", "agent_status", "approval", "state_update"
    data: dict
    timestamp: str = ""
