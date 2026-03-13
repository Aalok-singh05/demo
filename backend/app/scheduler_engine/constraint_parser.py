import json
from typing import List, Dict
from app.services.llm_service import get_llm


def parse_constraints(constraints: List[str]) -> List[Dict]:
    """
    Convert natural language constraints into structured rules
    that the constraint optimizer can understand.
    """

    if not constraints:
        return []

    llm = get_llm()

    prompt = f"""
You are a scheduling rule parser.

Convert natural language scheduling constraints into STRICT JSON.

Allowed rule types:

1. start_after
Example:
"Dr Sharma only available after 14:00"
→ {{"type": "start_after", "speaker": "Dr Sharma", "time": "14:00"}}

2. start_before
Example:
"Dr Mehta must speak before 12:00"
→ {{"type": "start_before", "speaker": "Dr Mehta", "time": "12:00"}}

3. must_be_on_day
Example:
"Keynote must be on Day 1"
→ {{"type": "must_be_on_day", "session_type": "keynote", "day": 1}}

4. cannot_be_on_day
Example:
"Workshops cannot be on Day 1"
→ {{"type": "cannot_be_on_day", "session_type": "workshop", "day": 1}}

5. preferred_venue
Example:
"Dr Sharma prefers Hall A"
→ {{"type": "preferred_venue", "speaker": "Dr Sharma", "venue": "Hall A"}}

Return ONLY valid JSON list.

Constraints:
{constraints}
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    try:
        return json.loads(content)

    except Exception:
        # fallback if model adds extra text
        try:
            start = content.index("[")
            end = content.rindex("]") + 1
            return json.loads(content[start:end])
        except Exception:
            return []