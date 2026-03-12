import copy
from datetime import datetime, timedelta
from app.scheduler_engine.conflict_detector import detect_conflicts


def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


def simulate_change(schedule, session_id, new_start_time):
    """
    Simulate moving a session to a new time without modifying the real schedule.
    """

    simulated_schedule = copy.deepcopy(schedule)

    moved_session = None

    for session in simulated_schedule:

        if session["session_id"] == session_id:

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
        "simulated_schedule": simulated_schedule,
        "moved_session": moved_session,
        "conflicts": conflicts
    }