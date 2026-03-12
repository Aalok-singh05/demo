from pydantic import BaseModel
from typing import Optional
from datetime import date as Date


class Venue(BaseModel):
    name: str
    capacity: int


class Session(BaseModel):
    session_id: str
    title: str
    speaker: str
    duration_minutes: int

    # NEW — multi‑day support
    day: int = 1
    date: Optional[Date] = None

    preferred_room: Optional[str] = None
    priority: int = 1


class ScheduledSession(BaseModel):
    session_id: str
    title: str
    speaker: str
    room: str

    # NEW — multi‑day support
    day: int
    date: Optional[Date] = None

    start_time: str
    end_time: str
    status: str


class Participant(BaseModel):
    participant_id: str
    name: str
    email: str
    role: str