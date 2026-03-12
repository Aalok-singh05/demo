# Schedule-related Pydantic models

from pydantic import BaseModel
from typing import Optional, List


class ScheduledSession(BaseModel):
    """A session that has been assigned a time and room."""
    id: str
    title: str
    session_type: str = "talk"
    speaker: Optional[str] = None
    venue: str
    day: int
    start_time: str
    end_time: str
    capacity: Optional[int] = None
    status: str = "scheduled"  # scheduled, moved, cancelled


class Conflict(BaseModel):
    """A scheduling conflict detected by Chronos."""
    type: str  # room_overlap, speaker_double_booking, time_violation
    severity: str  # hard, soft
    description: str
    sessions_involved: List[str] = []  # session IDs


class Resolution(BaseModel):
    """How a conflict was resolved."""
    conflict_type: str
    action_taken: str
    sessions_moved: List[str] = []
    participants_affected: int = 0


class ScheduleRequest(BaseModel):
    """Input to the Scheduler Agent."""
    event_name: str
    days: int = 1
    venues: List[dict] = []
    sessions: List[dict] = []
    constraints: List[str] = []  # natural language constraints
    fixed_slots: List[dict] = []


class ScheduleResult(BaseModel):
    """Output from the Scheduler Agent."""
    timeline: List[ScheduledSession] = []
    conflicts_found: List[Conflict] = []
    conflicts_resolved: List[Resolution] = []
    warnings: List[str] = []
    reasoning: str = ""
