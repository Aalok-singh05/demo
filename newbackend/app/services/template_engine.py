# Email template engine — {{placeholder}} personalization

import re
from typing import Dict, List, Any


def personalize_template(template: str, participant: Dict[str, Any]) -> str:
    """
    Replace {{placeholders}} in a template with participant data.
    Handles common field name variants automatically.
    """
    # Build a flat lookup with normalized keys
    lookup = {}
    for key, value in participant.items():
        lookup[key.lower()] = str(value) if value else ""
        lookup[key.lower().replace("_", " ")] = str(value) if value else ""

    # Also add first_name / last_name from "name" if available
    full_name = participant.get("name", "")
    if full_name:
        parts = full_name.strip().split()
        lookup["first_name"] = parts[0] if parts else ""
        lookup["first name"] = parts[0] if parts else ""
        lookup["last_name"] = parts[-1] if len(parts) > 1 else ""
        lookup["last name"] = parts[-1] if len(parts) > 1 else ""

    # Replace all {{placeholders}}
    def replace_match(match):
        key = match.group(1).strip().lower()
        return lookup.get(key, f"[{match.group(1).strip()}]")

    return re.sub(r'\{\{(.+?)\}\}', replace_match, template)


def personalize_batch(
    template: str,
    participants: List[Dict[str, Any]],
    preview_count: int = 3,
) -> Dict[str, Any]:
    """
    Personalize a template for a batch of participants.
    Returns a preview (first N) + stats.
    """
    previews = []
    for i, p in enumerate(participants):
        personalized = personalize_template(template, p)
        if i < preview_count:
            previews.append({
                "to": p.get("email", ""),
                "name": p.get("name", ""),
                "body": personalized,
            })

    return {
        "total": len(participants),
        "previews": previews,
        "template_used": template[:100] + "..." if len(template) > 100 else template,
    }
