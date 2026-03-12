from typing import List, Dict
from datetime import datetime, timedelta


def parse_time(time_str: str):
    return datetime.strptime(time_str, "%H:%M")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


def find_next_available_slot(schedule: List[Dict], room: str, day: int, duration_minutes: int):
    """
    Finds the next available slot in a given room on a specific day.
    """

    day_schedule = [
        s for s in schedule if s["room"] == room and s.get("day") == day
    ]

    schedule_sorted = sorted(day_schedule, key=lambda x: x["start_time"])

    for session in schedule_sorted:

        end_time = parse_time(session["end_time"])

        new_start = end_time
        new_end = new_start + timedelta(minutes=duration_minutes)

        conflict = False

        for s in schedule_sorted:

            s_start = parse_time(s["start_time"])
            s_end = parse_time(s["end_time"])

            if max(new_start, s_start) < min(new_end, s_end):
                conflict = True
                break

        if not conflict:
            return format_time(new_start), format_time(new_end)

    return None, None


def resolve_conflicts(schedule: List[Dict], conflicts: List[Dict]):

    resolutions = []

    # detect available rooms
    rooms = list({s["room"] for s in schedule})

    for conflict in conflicts:

        s1_id, s2_id = conflict["sessions"]

        s1 = next(s for s in schedule if s["session_id"] == s1_id)
        s2 = next(s for s in schedule if s["session_id"] == s2_id)

        # choose lower priority session to move
        if s1.get("priority", 1) <= s2.get("priority", 1):
            session_to_move = s1
        else:
            session_to_move = s2

        duration = (
            parse_time(session_to_move["end_time"])
            - parse_time(session_to_move["start_time"])
        ).seconds // 60

        original_day = session_to_move.get("day", 1)

        # ---- Strategy 1: same room same day ----
        new_start, new_end = find_next_available_slot(
            schedule,
            session_to_move["room"],
            original_day,
            duration
        )

        # ---- Strategy 2: different room same day ----
        if not new_start:

            for room in rooms:

                new_start, new_end = find_next_available_slot(
                    schedule,
                    room,
                    original_day,
                    duration
                )

                if new_start:
                    session_to_move["room"] = room
                    break

        # ---- Strategy 3: same room next day ----
        if not new_start:

            next_day = original_day + 1

            new_start, new_end = find_next_available_slot(
                schedule,
                session_to_move["room"],
                next_day,
                duration
            )

            if new_start:
                session_to_move["day"] = next_day

        # ---- Strategy 4: different room next day ----
        if not new_start:

            next_day = original_day + 1

            for room in rooms:

                new_start, new_end = find_next_available_slot(
                    schedule,
                    room,
                    next_day,
                    duration
                )

                if new_start:
                    session_to_move["room"] = room
                    session_to_move["day"] = next_day
                    break

        if new_start:

            old_start = session_to_move["start_time"]
            old_day = original_day

            session_to_move["start_time"] = new_start
            session_to_move["end_time"] = new_end

            resolutions.append({
                "session_id": session_to_move["session_id"],
                "old_day": old_day,
                "new_day": session_to_move["day"],
                "old_time": old_start,
                "new_time": new_start,
                "reason": conflict["type"]
            })

    return schedule, resolutions