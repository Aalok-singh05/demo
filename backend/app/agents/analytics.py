"""Athena — The Analytics Agent.

Provides data-driven insights about registration, capacity, and demographics.
Falls back to rule-based analysis if LLM is unavailable.
"""
from ..models.schemas import Insight
from .llm_helper import call_llm_json
import json


async def analyze_registrations(participants: list[dict], sessions: list[dict] = None) -> list[Insight]:
    """Analyze registration data and generate actionable insights.
    
    Args:
        participants: List of participant dicts.
        sessions: Optional list of session dicts for capacity analysis.
    
    Returns:
        List of Insight objects.
    """
    total = len(participants)
    valid = sum(1 for p in participants if p.get("status") == "valid")
    invalid = total - valid

    roles = {}
    for p in participants:
        role = p.get("role", "unknown").lower()
        roles[role] = roles.get(role, 0) + 1

    prompt = f"""You are Athena, the analytics intelligence for TechSummit 2026.

Analyze this registration data and provide 3-4 actionable insights:

Total registrants: {total}
Valid emails: {valid}
Invalid emails: {invalid}
Role breakdown: {json.dumps(roles)}
Registration target: 500

Sessions data: {json.dumps(sessions[:5] if sessions else [])}

Provide insights as JSON array:
[
    {{
        "type": "warning|info|success",
        "title": "Short title",
        "desc": "1-2 sentence description",
        "action": "Button text (e.g., 'Push Promo') or empty string"
    }}
]

Focus on: capacity warnings, registration velocity, audience composition, risk flags."""

    # Fallback insights based on actual data
    fallback = []
    
    if invalid > 0:
        fallback.append({
            "type": "warning",
            "title": "Invalid Emails Detected",
            "desc": f"{invalid} email addresses failed validation. These registrants won't receive communications.",
            "action": "Review List"
        })

    student_pct = roles.get("student", 0) / max(total, 1) * 100
    if student_pct > 30:
        fallback.append({
            "type": "success",
            "title": "Audience Insight",
            "desc": f"{student_pct:.0f}% of registrants are students. Highly engaged demographic.",
            "action": ""
        })

    if total < 500:
        gap = 500 - total
        fallback.append({
            "type": "info",
            "title": "Registration Velocity",
            "desc": f"Currently at {total}/500 target. Need {gap} more registrations.",
            "action": "Push Promo"
        })

    if not fallback:
        fallback = [
            {"type": "success", "title": "On Track", "desc": f"{total} registrants processed successfully.", "action": ""}
        ]

    result = await call_llm_json(prompt, fallback)

    insights = []
    items = result if isinstance(result, list) else fallback
    for i, item in enumerate(items):
        insights.append(Insight(
            id=i + 1,
            type=item.get("type", "info"),
            title=item.get("title", ""),
            desc=item.get("desc", ""),
            action=item.get("action", "")
        ))

    return insights
