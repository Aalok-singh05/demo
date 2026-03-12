from typing import List, Dict
from datetime import datetime, timedelta


def parse_time(time_str: str):
    return datetime.strptime(time_str, "%H:%M")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


def build_schedule(
    sessions: List[Dict],
    venues: List[Dict],
    start_time: str = "09:00",
    end_time: str = "18:00"
):
    """
    Intelligent multi‑day schedule builder.

    Features:
    - respects daily time window
    - automatically moves overflow sessions to next day
    - supports multiple rooms
    - schedules by priority
    """

    start_dt = parse_time(start_time)
    end_dt = parse_time(end_time)

    schedule = []

    # sort by priority
    sessions_sorted = sorted(
        sessions,
        key=lambda x: x.get("priority", 1),
        reverse=True
    )

    current_day = 1
    current_time = start_dt
    venue_index = 0

    for session in sessions_sorted:

        duration = session.get("duration_minutes", 60)

        proposed_end = current_time + timedelta(minutes=duration)

        # if session exceeds day limit → move to next day
        if proposed_end > end_dt:

            current_day += 1
            current_time = start_dt
            venue_index = 0

            proposed_end = current_time + timedelta(minutes=duration)

        room = venues[venue_index]["name"]

        scheduled_session = {
            "session_id": session["session_id"],
            "title": session["title"],
            "speaker": session["speaker"],
            "room": room,
            "day": current_day,
            "start_time": format_time(current_time),
            "end_time": format_time(proposed_end),
            "priority": session.get("priority", 1),
            "status": "upcoming"
        }

        schedule.append(scheduled_session)

        venue_index += 1

        # rotate rooms
        if venue_index >= len(venues):
            venue_index = 0
            current_time = proposed_end

    return schedule