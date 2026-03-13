# ============================================================================
# NEXUS BACKEND — Schedule Pydantic Models
# ============================================================================
# Chronos Scheduler Agent Schema
# Defines structured inputs and outputs for timeline generation,
# conflict detection, and autonomous resolution.
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List


# ============================================================================
# CORE INPUT MODELS
# ============================================================================

class Venue(BaseModel):
    """
    Represents a physical location where sessions can occur.
    """
    name: str = Field(..., description="Venue name (e.g., Hall A)")
    capacity: Optional[int] = Field(None, description="Maximum number of attendees allowed")


class Session(BaseModel):
    """
    Represents a session before scheduling.
    """
    id: str = Field(..., description="Unique identifier for the session")
    title: str = Field(..., description="Title of the session")
    speaker: Optional[str] = Field(None, description="Speaker name")

    duration_minutes: int = Field(
        60,
        description="Length of the session"
    )

    session_type: str = Field(
        "talk",
        description="Type of session (talk, workshop, keynote, break)"
    )

    priority: int = Field(
        1,
        description="Priority level used during conflict resolution (higher = more important)"
    )


class FixedSlot(BaseModel):
    """
    Represents sessions that cannot be moved (opening ceremony, lunch etc.)
    """
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Name of the fixed event")

    venue: str = Field(..., description="Assigned venue")

    day: int = Field(..., description="Day number (1-indexed)")
    start_time: str = Field(..., description="Start time HH:MM")
    end_time: str = Field(..., description="End time HH:MM")


# ============================================================================
# SCHEDULE OUTPUT MODELS
# ============================================================================

class ScheduledSession(BaseModel):
    """
    Represents a finalized scheduled session on the timeline.
    """
    id: str = Field(..., description="Unique session identifier")
    title: str = Field(..., description="Title of the session")

    session_type: str = Field(
        "talk",
        description="Type (talk, workshop, keynote, break)"
    )

    speaker: Optional[str] = Field(
        None,
        description="Name of the speaker"
    )

    venue: str = Field(
        ...,
        description="Assigned venue"
    )

    day: int = Field(
        ...,
        description="Day of the event (1-indexed)"
    )

    start_time: str = Field(
        ...,
        description="Start time formatted as HH:MM"
    )

    end_time: str = Field(
        ...,
        description="End time formatted as HH:MM"
    )

    capacity: Optional[int] = Field(
        None,
        description="Venue capacity"
    )

    status: str = Field(
        "scheduled",
        description="Status: scheduled | moved | cancelled"
    )


# ============================================================================
# CONFLICT SYSTEM
# ============================================================================

class Conflict(BaseModel):
    """
    Represents a scheduling conflict detected by Chronos.
    """
    type: str = Field(
        ...,
        description="Type: room_overlap | speaker_double_booking | constraint_violation"
    )

    severity: str = Field(
        ...,
        description="hard (must fix) or soft (warning)"
    )

    description: str = Field(
        ...,
        description="Human readable explanation"
    )

    sessions_involved: List[str] = Field(
        default_factory=list,
        description="IDs of sessions involved"
    )


class Resolution(BaseModel):
    """
    Represents an automated fix Chronos applied.
    """

    conflict_type: str = Field(
        ...,
        description="Conflict type that was resolved"
    )

    action_taken: str = Field(
        ...,
        description="Explanation of the resolution"
    )

    sessions_moved: List[str] = Field(
        default_factory=list,
        description="Sessions that changed time/venue"
    )

    participants_affected: int = Field(
        0,
        description="Estimated number of attendees impacted"
    )


# ============================================================================
# AGENT REQUEST / RESPONSE
# ============================================================================

class ScheduleRequest(BaseModel):
    """
    Input payload sent to Chronos agent.
    """

    event_name: str = Field(
        ...,
        description="Name of the event"
    )

    days: int = Field(
        1,
        description="Total number of event days"
    )

    venues: List[Venue] = Field(
        default_factory=list,
        description="Available venues"
    )

    sessions: List[Session] = Field(
        default_factory=list,
        description="Sessions to schedule"
    )

    constraints: List[str] = Field(
        default_factory=list,
        description="Natural language rules"
    )

    fixed_slots: List[FixedSlot] = Field(
        default_factory=list,
        description="Immovable events"
    )


class ScheduleResult(BaseModel):
    """
    Output produced by Chronos after building the schedule.
    """

    timeline: List[ScheduledSession] = Field(
        default_factory=list,
        description="Final event schedule"
    )

    conflicts_found: List[Conflict] = Field(
        default_factory=list,
        description="Conflicts detected during planning"
    )

    conflicts_resolved: List[Resolution] = Field(
        default_factory=list,
        description="Actions Chronos took to resolve conflicts"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Soft issues that did not require fixing"
    )

    reasoning: str = Field(
        "",
        description="Explanation of scheduling decisions"
    )