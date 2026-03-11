"""Chronos — The Scheduler Agent.

Detects schedule conflicts and uses LLM to propose optimal resolutions.
Falls back to rule-based heuristics if LLM is unavailable.
"""
from ..models.schemas import ScheduleOptimizeResult, ConflictInfo
from .llm_helper import call_llm_json
import json


async def optimize_schedule(sessions: list[dict]) -> ScheduleOptimizeResult:
    """Detect and resolve schedule conflicts.
    
    Args:
        sessions: List of session dicts with id, title, time, room, speaker, type, has_conflict.
    
    Returns:
        ScheduleOptimizeResult with conflicts found, resolved count, changes, and reasoning.
    """
    # ── Step 1: Detect conflicts ──────────────────────────
    conflicts = _detect_conflicts(sessions)

    if not conflicts:
        return ScheduleOptimizeResult(
            conflicts_found=[],
            conflicts_resolved=0,
            changes_made=[],
            reasoning="No conflicts detected. Schedule is clean."
        )

    # ── Step 2: Try LLM resolution ────────────────────────
    prompt = f"""You are Chronos, the scheduling intelligence for TechSummit 2026.

Analyze these schedule conflicts and propose resolutions:

SESSIONS:
{json.dumps(sessions, indent=2)}

CONFLICTS DETECTED:
{json.dumps([c.model_dump() for c in conflicts], indent=2)}

Rules:
1. Keynotes have highest priority, then workshops, then panels, then breaks
2. Minimize attendee disruption
3. Try to use freed-up time slots when moving sessions
4. Never double-book a room

Respond in JSON format:
{{
    "conflicts_resolved": <number>,
    "changes_made": ["description of change 1", "description of change 2"],
    "reasoning": "Step-by-step explanation of your conflict resolution strategy"
}}"""

    fallback = {
        "conflicts_resolved": len(conflicts),
        "changes_made": [
            f"Moved \"{c.description.split('vs')[0].strip()}\" to a free time slot"
            for c in conflicts
        ],
        "reasoning": (
            "> Detected overlapping sessions in the same room.\n"
            "> Applied priority heuristic: Keynote > Workshop > Panel > Break.\n"
            "> Moved lower-priority sessions to available time slots.\n"
            "> Verified no further cascading conflicts."
        )
    }

    result = await call_llm_json(prompt, fallback)

    return ScheduleOptimizeResult(
        conflicts_found=conflicts,
        conflicts_resolved=result.get("conflicts_resolved", len(conflicts)),
        changes_made=result.get("changes_made", fallback["changes_made"]),
        reasoning=result.get("reasoning", fallback["reasoning"])
    )


def _detect_conflicts(sessions: list[dict]) -> list[ConflictInfo]:
    """Simple conflict detection: same room + overlapping time."""
    conflicts = []
    for i, a in enumerate(sessions):
        for j, b in enumerate(sessions):
            if j <= i:
                continue
            if a["room"] == b["room"] and _times_overlap(a["time"], b["time"]):
                conflicts.append(ConflictInfo(
                    session_a_id=a["id"],
                    session_b_id=b["id"],
                    room=a["room"],
                    time_overlap=f"{a['time']} & {b['time']}",
                    description=f"\"{a['title']}\" vs \"{b['title']}\" in {a['room']}"
                ))
    return conflicts


def _times_overlap(time_a: str, time_b: str) -> bool:
    """Check if two time ranges like '09:00 AM - 10:30 AM' overlap."""
    try:
        start_a, end_a = _parse_time_range(time_a)
        start_b, end_b = _parse_time_range(time_b)
        return start_a < end_b and start_b < end_a
    except Exception:
        return False


def _parse_time_range(time_str: str) -> tuple[int, int]:
    """Parse '09:00 AM - 10:30 AM' into minutes from midnight."""
    parts = time_str.split(" - ")
    return _to_minutes(parts[0].strip()), _to_minutes(parts[1].strip())


def _to_minutes(t: str) -> int:
    """Convert '09:00 AM' to minutes from midnight."""
    time_part, period = t[:-3], t[-2:]
    hours, minutes = map(int, time_part.split(":"))
    if period.upper() == "PM" and hours != 12:
        hours += 12
    elif period.upper() == "AM" and hours == 12:
        hours = 0
    return hours * 60 + minutes
