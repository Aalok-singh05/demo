# Agent communication Pydantic models

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AgentMessage(BaseModel):
    """An inter-agent message (displayed in the activity panel)."""
    from_agent: str
    to_agent: str
    message_type: str = "notification"  # request, notification, data_share
    priority: str = "normal"  # critical, normal, low
    payload: dict = {}
    requires_response: bool = False
    timestamp: str = ""
    trace_id: str = ""


class ApprovalItem(BaseModel):
    """An item requiring organizer approval before execution."""
    id: str
    agent: str
    action: str
    description: str
    impact: str = ""
    preview: dict = {}
    options: List[str] = ["approve", "edit", "reject"]
    status: str = "pending"
    created_at: str = ""


class WSMessage(BaseModel):
    """WebSocket message sent to the frontend."""
    type: str  # agent_status, agent_complete, agent_message, approval_request, state_update, error
    data: dict = {}
    timestamp: str = ""


class AgentStatus(BaseModel):
    """Current status of an agent."""
    agent: str
    status: str = "idle"  # idle, working, done, error
    last_task: Optional[str] = None
    last_active: Optional[str] = None
