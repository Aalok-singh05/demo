# Event-related Pydantic models

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Venue(BaseModel):
    """A room/venue where sessions can be held."""
    name: str
    capacity: int
    location: Optional[str] = None
    has_projector: bool = True
    has_wifi: bool = True


class Session(BaseModel):
    """A session (talk, workshop, break) to be scheduled."""
    title: str
    description: Optional[str] = None
    session_type: str = "talk"  # talk, workshop, break, keynote, panel
    speaker: Optional[str] = None
    duration_minutes: int = 60
    preferred_venue: Optional[str] = None
    day: Optional[int] = None
    capacity: Optional[int] = None


class FixedSlot(BaseModel):
    """An immovable item in the schedule (opening ceremony, etc.)."""
    title: str
    venue: str
    day: int
    start_time: str  # "09:00"
    end_time: str    # "10:00"


class EventCreate(BaseModel):
    """Schema for creating a new event."""
    name: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    organizer_name: Optional[str] = None
    venues: Optional[List[Venue]] = []
    days: int = 1


class EventUpdate(BaseModel):
    """Schema for updating an event (all fields optional)."""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    organizer_name: Optional[str] = None
    status: Optional[str] = None


class Event(BaseModel):
    """Full event model."""
    id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    organizer_name: Optional[str] = None
    status: str = "draft"
    venues: List[Venue] = []
    days: int = 1
    config: dict = {}
    created_at: str = ""
    updated_at: str = ""
