import json

from app.schemas.apollo_schema import ContentRequest, ContentResult, ContentPiece
from app.services.llm_service import get_llm
from app.services.engagement_analyzer import analyze_engagement_csv


def generate_content(request: ContentRequest):

    llm = get_llm()

    prompt = f"""
You are Apollo, the creative marketing strategist for tech events.

Create promotional social media content.

Event Description:
{request.event_description}

Target Audience:
{request.target_audience}

Platform:
{request.platform}

Return STRICT JSON in this format:

[
  {{
    "tone": "professional",
    "text": "post text",
    "suggested_time": "18:00",
    "image_prompt": "poster prompt"
  }},
  {{
    "tone": "casual",
    "text": "post text",
    "suggested_time": "18:00",
    "image_prompt": "poster prompt"
  }},
  {{
    "tone": "hype",
    "text": "post text",
    "suggested_time": "18:00",
    "image_prompt": "poster prompt"
  }}
]

Rules:
- Only return JSON
- No markdown
- No explanations
"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    # ---- Safe JSON parsing ----
    try:
        data = json.loads(content)
    except Exception:
        try:
            start = content.index("[")
            end = content.rindex("]") + 1
            json_part = content[start:end]
            data = json.loads(json_part)
        except Exception:
            data = []

    pieces = []

    for item in data:

        pieces.append(
            ContentPiece(
                platform=request.platform or "general",
                text=item.get("text", ""),
                suggested_time=item.get("suggested_time", "18:00"),
                image_prompt=item.get("image_prompt", "")
            )
        )

    return pieces


def plan_campaign(request: ContentRequest):

    llm = get_llm()

    prompt = f"""
You are Apollo, a marketing strategist.

Create a campaign timeline for promoting this event.

Event:
{request.event_description}

Build a narrative campaign arc:

Teaser → Speaker Reveal → Workshop Highlights → Countdown → Launch → Recap

Return a list of posts with suggested days.
"""

    response = llm.invoke(prompt)

    timeline = response.content.split("\n")

    return timeline


def analyze_engagement(request: ContentRequest):

    if not request.historical_data:
        return "No historical engagement data provided."

    data_summary = analyze_engagement_csv(request.historical_data)

    llm = get_llm()

    prompt = f"""
You are a social media analytics expert.

Analyze this engagement summary.

Data:
{data_summary}

Provide insights:

- Best day to post
- Best time of day
- Best performing platform
- Best type of content
"""

    response = llm.invoke(prompt)

    return response.content


def update_content(request: ContentRequest):

    llm = get_llm()

    prompt = f"""
Update promotional content due to schedule or event change.

Event:
{request.event_description}

Content ID:
{request.existing_content_id}

Return promotional text and a poster prompt.
"""

    response = llm.invoke(prompt)

    piece = ContentPiece(
        platform=request.platform or "general",
        text=response.content,
        suggested_time="18:00",
        image_prompt=f"Updated promotional poster for {request.event_description}"
    )

    return [piece]


def apollo_agent(request: ContentRequest):

    content_pieces = []
    campaign_timeline = None
    engagement_insights = None

    if request.action == "generate":
        content_pieces = generate_content(request)

    elif request.action == "plan_campaign":
        campaign_timeline = plan_campaign(request)

    elif request.action == "analyze_timing":
        engagement_insights = analyze_engagement(request)

    elif request.action == "update_content":
        content_pieces = update_content(request)

    reasoning = "Apollo generated marketing content, campaign strategy, and engagement insights."

    return ContentResult(
        content_pieces=content_pieces,
        campaign_timeline=campaign_timeline,
        engagement_insights=engagement_insights,
        reasoning=reasoning
    )