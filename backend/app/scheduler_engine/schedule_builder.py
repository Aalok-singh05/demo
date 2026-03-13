from datetime import datetime, timedelta
from typing import List
from app.schemas.chronos_schema import Session, Venue, FixedSlot


def parse_time(time_str: str):
    return datetime.strptime(time_str, "%H:%M")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


def overlaps(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)


def slot_available(schedule, venue, day, start_time, end_time):
    """
    Check whether a venue is free during a time window.
    """

    for s in schedule:

        if s["day"] != day:
            continue

        if s["venue"] != venue:
            continue

        s_start = parse_time(s["start_time"])
        s_end = parse_time(s["end_time"])

        if overlaps(start_time, end_time, s_start, s_end):
            return False

    return True


def build_schedule(
    sessions: List[Session],
    venues: List[Venue],
    fixed_slots: List[FixedSlot],
    days: int,
    start_time: str = "09:00",
    end_time: str = "18:00",
):
    """
    Build initial clean schedule.
    """

    schedule = []

    start_dt = parse_time(start_time)
    end_dt = parse_time(end_time)

    # ------------------------------------------------
    # PASS 1 — ADD FIXED SLOTS
    # ------------------------------------------------

    for slot in fixed_slots:

        schedule.append(
            {
                "id": slot.id,
                "title": slot.title,
                "session_type": "fixed",
                "speaker": None,
                "venue": slot.venue,
                "day": slot.day,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "status": "scheduled",
            }
        )

    # ------------------------------------------------
    # PASS 2 — SORT BY PRIORITY
    # ------------------------------------------------

    sessions_sorted = sorted(
        sessions,
        key=lambda s: s.priority,
        reverse=True,
    )

    # ------------------------------------------------
    # PASS 3 — SCHEDULE SESSIONS
    # ------------------------------------------------

    for session in sessions_sorted:

        duration = timedelta(minutes=session.duration_minutes)

        placed = False

        for day in range(1, days + 1):

            current_time = start_dt

            while current_time + duration <= end_dt:

                proposed_end = current_time + duration

                for venue in venues:

                    if slot_available(
                        schedule,
                        venue.name,
                        day,
                        current_time,
                        proposed_end,
                    ):

                        schedule.append(
                            {
                                "id": session.id,
                                "title": session.title,
                                "session_type": session.session_type,
                                "speaker": session.speaker,
                                "venue": venue.name,
                                "day": day,
                                "start_time": format_time(current_time),
                                "end_time": format_time(proposed_end),
                                "status": "scheduled",
                                "priority": session.priority,
                            }
                        )

                        placed = True
                        break

                if placed:
                    break

                current_time += timedelta(minutes=30)

            if placed:
                break

    return schedule