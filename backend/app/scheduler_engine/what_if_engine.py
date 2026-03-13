import copy
from typing import List, Dict, Any
from datetime import datetime

from app.scheduler_engine.conflict_detector import detect_conflicts
from app.scheduler_engine.resolution_engine import resolve_conflicts


def parse_time(time_str: str):
    return datetime.strptime(time_str, "%H:%M")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


# ==========================================================
# STEP 1 — SIMULATE CHANGE
# ==========================================================

def simulate_change(
    schedule: List[Dict],
    session_id: str,
    new_start_time: str
) -> Dict[str, Any]:
    """
    Simulate moving a session without modifying the real schedule.
    """

    simulated_schedule = copy.deepcopy(schedule)

    moved_session = None

    for session in simulated_schedule:

        if session["id"] == session_id:

            start_dt = parse_time(session["start_time"])
            end_dt = parse_time(session["end_time"])

            duration = end_dt - start_dt

            new_start_dt = parse_time(new_start_time)
            new_end_dt = new_start_dt + duration

            session["start_time"] = format_time(new_start_dt)
            session["end_time"] = format_time(new_end_dt)

            moved_session = session
            break

    conflicts = detect_conflicts(simulated_schedule)

    return {
        "status": "simulation_complete",
        "moved_session": moved_session,
        "simulated_schedule": simulated_schedule,
        "conflicts_found": conflicts,
        "requires_resolution": len(conflicts) > 0
    }


# ==========================================================
# STEP 2 — RESOLVE SIMULATION
# ==========================================================

def resolve_simulation(
    simulated_schedule: List[Dict],
    conflicts,
    venues: List[str],
    days: int,
    current_day: int = 1
):
    """
    Resolve conflicts generated during simulation.
    """

    updated_schedule, resolutions = resolve_conflicts(
        simulated_schedule,
        conflicts,
        venues,
        days,
        current_day
    )

    return {
        "status": "resolution_complete",
        "updated_schedule": updated_schedule,
        "resolutions": resolutions
    }


# ==========================================================
# STEP 3 — APPLY CHANGE (FINAL COMMIT)
# ==========================================================

def commit_simulation(
    current_schedule: List[Dict],
    approved_schedule: List[Dict]
):
    """
    Replace the current schedule with the approved simulated schedule.
    """

    return {
        "status": "schedule_updated",
        "new_schedule": approved_schedule
    }