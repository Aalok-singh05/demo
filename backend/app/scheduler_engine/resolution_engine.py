from typing import List, Dict
from datetime import datetime, timedelta
from app.schemas.chronos_schema import Resolution


def parse_time(time_str: str):
    return datetime.strptime(time_str, "%H:%M")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


def overlaps(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)


def venue_available(schedule, venue, day, start, end, ignore_id=None):

    for s in schedule:

        if s["id"] == ignore_id:
            continue

        if s["day"] != day:
            continue

        if s["venue"] != venue:
            continue

        s_start = parse_time(s["start_time"])
        s_end = parse_time(s["end_time"])

        if overlaps(start, end, s_start, s_end):
            return False

    return True


def speaker_available(schedule, speaker, day, start, end, ignore_id=None):

    if not speaker:
        return True

    for s in schedule:

        if s["id"] == ignore_id:
            continue

        if s["day"] != day:
            continue

        if s.get("speaker") != speaker:
            continue

        s_start = parse_time(s["start_time"])
        s_end = parse_time(s["end_time"])

        if overlaps(start, end, s_start, s_end):
            return False

    return True


def resolve_conflicts(
    schedule: List[Dict],
    conflicts: List[Dict],
    venues: List[str],
    days: int,
    current_day: int = 1,
):

    resolutions = []

    for conflict in conflicts:

        s1_id, s2_id = conflict.sessions_involved

        s1 = next(s for s in schedule if s["id"] == s1_id)
        s2 = next(s for s in schedule if s["id"] == s2_id)

        # Move lower priority session
        if s1.get("priority", 1) <= s2.get("priority", 1):
            move_session = s1
        else:
            move_session = s2

        duration = (
            parse_time(move_session["end_time"])
            - parse_time(move_session["start_time"])
        )

        original_day = move_session["day"]
        original_start = parse_time(move_session["start_time"])

        moved = False

        # ------------------------------------------------
        # STRATEGY 1 — move later same venue
        # ------------------------------------------------

        new_start = original_start + timedelta(minutes=30)

        while new_start.time() < datetime.strptime("18:00", "%H:%M").time():

            new_end = new_start + duration

            if venue_available(
                schedule,
                move_session["venue"],
                original_day,
                new_start,
                new_end,
                move_session["id"],
            ) and speaker_available(
                schedule,
                move_session.get("speaker"),
                original_day,
                new_start,
                new_end,
                move_session["id"],
            ):

                move_session["start_time"] = format_time(new_start)
                move_session["end_time"] = format_time(new_end)
                move_session["status"] = "moved"

                moved = True
                break

            new_start += timedelta(minutes=30)

        # ------------------------------------------------
        # STRATEGY 2 — different venue same time
        # ------------------------------------------------

        if not moved:

            start = parse_time(move_session["start_time"])
            end = parse_time(move_session["end_time"])

            for venue in venues:

                if venue == move_session["venue"]:
                    continue

                if venue_available(schedule, venue, original_day, start, end):

                    move_session["venue"] = venue
                    move_session["status"] = "moved"

                    moved = True
                    break

        # ------------------------------------------------
        # STRATEGY 3 — next day
        # ------------------------------------------------

        if not moved:

            for day in range(max(original_day, current_day), days + 1):

                start = datetime.strptime("09:00", "%H:%M")
                end = start + duration

                for venue in venues:

                    if venue_available(schedule, venue, day, start, end):

                        move_session["venue"] = venue
                        move_session["day"] = day
                        move_session["start_time"] = format_time(start)
                        move_session["end_time"] = format_time(end)
                        move_session["status"] = "moved"

                        moved = True
                        break

                if moved:
                    break

        if moved:

            resolutions.append(
                Resolution(
                    conflict_type=conflict.type,
                    action_taken=f"Moved session {move_session['id']} to {move_session['venue']} on Day {move_session['day']} at {move_session['start_time']}",
                    sessions_moved=[move_session["id"]],
                    participants_affected=0,
                )
            )

    return schedule, resolutions