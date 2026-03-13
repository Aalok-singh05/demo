from typing import List, Dict
from datetime import datetime
from app.schemas.chronos_schema import Conflict


def parse_time(time_str: str):
    return datetime.strptime(time_str, "%H:%M")


def sessions_overlap(start1, end1, start2, end2):
    """
    Check if two time intervals overlap.
    """
    return max(start1, start2) < min(end1, end2)


def detect_conflicts(schedule: List[Dict]) -> List[Conflict]:
    """
    Scan the schedule and detect HARD conflicts.

    Detects:
    - room_overlap
    - speaker_double_booking
    """

    conflicts: List[Conflict] = []

    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):

            s1 = schedule[i]
            s2 = schedule[j]

            # Only compare sessions on the same day
            if s1["day"] != s2["day"]:
                continue

            start1 = parse_time(s1["start_time"])
            end1 = parse_time(s1["end_time"])

            start2 = parse_time(s2["start_time"])
            end2 = parse_time(s2["end_time"])

            if not sessions_overlap(start1, end1, start2, end2):
                continue

            # ------------------------------------------------
            # ROOM / VENUE CONFLICT
            # ------------------------------------------------

            if s1["venue"] == s2["venue"]:

                conflicts.append(
                    Conflict(
                        type="room_overlap",
                        severity="hard",
                        description="Two sessions scheduled in the same venue at the same time",
                        sessions_involved=[s1["id"], s2["id"]],
                    )
                )

            # ------------------------------------------------
            # SPEAKER DOUBLE BOOKING
            # ------------------------------------------------

            if (
                s1.get("speaker")
                and s2.get("speaker")
                and s1["speaker"] == s2["speaker"]
            ):

                conflicts.append(
                    Conflict(
                        type="speaker_double_booking",
                        severity="hard",
                        description=f"{s1['speaker']} is scheduled for two sessions at the same time",
                        sessions_involved=[s1["id"], s2["id"]],
                    )
                )

    return conflicts