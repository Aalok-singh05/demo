# Participant-related Pydantic models

from pydantic import BaseModel, Field
from typing import Optional, List


class Participant(BaseModel):
    """A registered participant."""
    name: str
    email: str
    role: str = "attendee"  # attendee, speaker, volunteer, organizer
    track: Optional[str] = None
    organization: Optional[str] = None
    phone: Optional[str] = None
    is_valid_email: bool = True
    metadata: dict = {}


class InvalidEmail(BaseModel):
    """An invalid email entry found during CSV parsing."""
    email: str
    name: str = ""
    reason: str = "Invalid format"


class Segment(BaseModel):
    """A group of participants filtered by criteria."""
    name: str
    criteria: str
    count: int
    participant_emails: List[str] = []


class ParticipantUploadResult(BaseModel):
    """Result of parsing a participant CSV/Excel file."""
    total: int
    valid: int
    invalid: int
    duplicates: int = 0
    invalid_details: List[InvalidEmail] = []
    participants: List[Participant] = []
    columns_found: List[str] = []
