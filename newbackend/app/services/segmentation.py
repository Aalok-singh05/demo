# Participant segmentation service

from typing import List, Dict, Any


def segment_by_field(participants: List[Dict], field: str) -> Dict[str, List[Dict]]:
    """
    Group participants by a specific field value.
    Example: segment_by_field(participants, "role") →
      {"attendee": [...], "speaker": [...], "volunteer": [...]}
    """
    segments = {}
    for p in participants:
        value = str(p.get(field, "unknown")).strip().lower() or "unknown"
        if value not in segments:
            segments[value] = []
        segments[value].append(p)
    return segments


def segment_by_criteria(participants: List[Dict], criteria: str) -> List[Dict]:
    """
    Filter participants by natural language criteria.
    Supports simple keyword matching for hackathon scope.
    """
    criteria_lower = criteria.lower()

    # Role-based filtering
    roles = ["speaker", "attendee", "volunteer", "organizer"]
    for role in roles:
        if role in criteria_lower:
            return [p for p in participants if p.get("role", "").lower() == role]

    # Track-based filtering
    if "track" in criteria_lower:
        track_name = criteria_lower.replace("track", "").strip()
        return [p for p in participants if track_name in p.get("track", "").lower()]

    # Valid/invalid email filtering
    if "invalid" in criteria_lower:
        return [p for p in participants if not p.get("is_valid_email", True)]
    if "valid" in criteria_lower:
        return [p for p in participants if p.get("is_valid_email", True)]

    # Default: return all
    return participants


def create_segment_summary(segments: Dict[str, List[Dict]]) -> List[Dict]:
    """Convert segment dict to a list of summary dicts for the API."""
    return [
        {"name": name, "count": len(members), "criteria": f"field={name}"}
        for name, members in segments.items()
    ]
