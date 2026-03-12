from pydantic import BaseModel
from typing import List, Optional, Dict

from app.schemas.shared_models import Venue, Session, ScheduledSession


class ScheduleRequest(BaseModel):

    event_name: str
    days: int
    venues: List[Venue]
    sessions: List[Session]

    constraints: List[str] = []
    fixed_slots: List[str] = []

    # NEW: allows what-if simulation requests
    what_if: Optional[Dict] = None


class ScheduleResult(BaseModel):

    timeline: List[ScheduledSession]

    conflicts_found: List[str]

    conflicts_resolved: List[str]

    warnings: List[str]

    affected_participants: List[str]

    cascade_to: List[str]

    reasoning: str

    # Already added earlier
    simulation: Optional[Dict] = None