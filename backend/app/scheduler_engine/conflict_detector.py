from typing import List, Dict
from datetime import datetime


def parse_time(time_str: str):
    """
    Convert time string (HH:MM) to datetime object.
    """
    return datetime.strptime(time_str, "%H:%M")


def sessions_overlap(start1, end1, start2, end2):
    """
    Check if two time ranges overlap.
    """
    return max(start1, start2) < min(end1, end2)


def detect_conflicts(schedule: List[Dict]):
    """
    Detect scheduling conflicts in the timeline.

    schedule example item:
    {
        "session_id": "S1",
        "title": "AI Ethics",
        "speaker": "Dr Sharma",
        "room": "Hall A",
        "day": 1,
        "start_time": "10:00",
        "end_time": "11:00"
    }
    """

    conflicts = []

    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):

            s1 = schedule[i]
            s2 = schedule[j]

            # 🔹 NEW — only compare sessions on same day
            if s1.get("day") != s2.get("day"):
                continue

            start1 = parse_time(s1["start_time"])
            end1 = parse_time(s1["end_time"])

            start2 = parse_time(s2["start_time"])
            end2 = parse_time(s2["end_time"])

            if sessions_overlap(start1, end1, start2, end2):

                # room conflict
                if s1["room"] == s2["room"]:
                    conflicts.append({
                        "type": "ROOM_CONFLICT",
                        "day": s1["day"],
                        "sessions": [s1["session_id"], s2["session_id"]],
                        "reason": "Two sessions scheduled in same room"
                    })

                # speaker conflict
                if s1["speaker"] == s2["speaker"]:
                    conflicts.append({
                        "type": "SPEAKER_CONFLICT",
                        "day": s1["day"],
                        "sessions": [s1["session_id"], s2["session_id"]],
                        "reason": "Speaker double-booked"
                    })

    return conflicts