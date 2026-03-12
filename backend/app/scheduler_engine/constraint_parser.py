import json
from app.services.llm_service import get_llm


def parse_constraints(constraints):
    """
    Convert natural language constraints into structured rules.
    """

    if not constraints:
        return []

    llm = get_llm()

    prompt = f"""
You are a scheduling rules parser.

Convert the following constraints into STRICT JSON.

Allowed rule types:
- start_after
- start_before
- must_be_on_day
- cannot_be_on_day
- preferred_room

Return ONLY valid JSON.

Example output:

[
  {{
    "speaker": "Dr Sharma",
    "type": "start_after",
    "time": "14:00"
  }}
]

Constraints:
{constraints}
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    try:
        parsed = json.loads(content)
        return parsed

    except Exception:
        # fallback if model adds text before JSON
        try:
            start = content.index("[")
            end = content.rindex("]") + 1
            json_part = content[start:end]
            return json.loads(json_part)
        except Exception:
            return []