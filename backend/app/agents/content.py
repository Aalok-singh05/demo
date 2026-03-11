"""Apollo — The Content Strategist Agent.

Generates platform-specific promotional content using LLM.
Falls back to template-based content if LLM is unavailable.
"""
from ..models.schemas import GenerateResult, ContentPiece, ContentQueueItem
from .llm_helper import call_llm_json
import json


async def generate_content(
    brief: str, platforms: list[str], tone: str
) -> GenerateResult:
    """Generate promotional content variants for specified platforms.
    
    Args:
        brief: Campaign brief / event description.
        platforms: Target platforms (e.g., ['linkedin', 'twitter']).
        tone: Desired tone ('professional', 'hype', 'technical', 'auto').
    
    Returns:
        GenerateResult with content variants, campaign timeline, and reasoning.
    """
    prompt = f"""You are Apollo, the creative marketing mind for TechSummit 2026.

Generate promotional content based on this brief:
"{brief}"

Target platforms: {', '.join(platforms)}
Tone: {tone}

For EACH platform, generate a compelling post. Include:
- Main text (appropriate length for the platform)
- Relevant hashtags
- An image description prompt for AI image generation

Also suggest a 3-step campaign timeline: Teaser → Main Push → Follow-up.

Respond in JSON:
{{
    "variants": [
        {{
            "platform": "linkedin",
            "tone": "{tone}",
            "text": "...",
            "image_prompt": "...",
            "is_recommended": true
        }}
    ],
    "campaign_timeline": [
        {{"label": "Teaser", "time": "Today 2PM", "type": "teaser"}},
        {{"label": "Speaker Bio", "time": "Tomorrow 9AM", "type": "speaker_bio"}},
        {{"label": "Live Update", "time": "Day of Event", "type": "live_update"}}
    ],
    "reasoning": "Explanation of creative strategy and platform adaptation choices"
}}"""

    # Fallback content
    fallback_variants = []
    platform_templates = {
        "linkedin": {
            "tone": "professional",
            "text": f"We're excited to share some big updates from our upcoming event.\n\n{brief}\n\nStay tuned for more details. This is going to be a landmark gathering for the tech community.\n\n#TechSummit2026 #Innovation #AI #Technology",
            "image_prompt": "A professional conference banner with modern tech aesthetics and blue lighting",
            "is_recommended": True,
        },
        "twitter": {
            "tone": "hype",
            "text": f"🚨 BIG NEWS! 🚨\n\n{brief[:180]}\n\nYou don't want to miss this! 🔥\n\nSecure your spot now! 👇\n#TechSummit2026",
            "image_prompt": "An energetic tech event banner with bold colors and dynamic typography",
            "is_recommended": False,
        },
        "instagram": {
            "tone": "casual",
            "text": f"✨ Something incredible is coming ✨\n\n{brief[:200]}\n\nTag someone who needs to see this! 👇\n\n#TechSummit2026 #TechEvent #Innovation",
            "image_prompt": "A visually stunning square image with gradient backgrounds and tech icons",
            "is_recommended": False,
        },
        "email": {
            "tone": "professional",
            "text": f"Dear Attendee,\n\n{brief}\n\nWe look forward to welcoming you at TechSummit 2026.\n\nBest regards,\nThe TechSummit Team",
            "image_prompt": "A clean email header banner with the TechSummit 2026 logo",
            "is_recommended": False,
        },
    }

    for i, platform in enumerate(platforms):
        pt = platform.lower().replace("/x", "").replace("x", "twitter").strip()
        template = platform_templates.get(pt, platform_templates["linkedin"])
        fallback_variants.append({
            "platform": platform,
            "tone": template["tone"] if tone == "auto" else tone,
            "text": template["text"],
            "image_prompt": template["image_prompt"],
            "is_recommended": i == 0,
        })

    fallback = {
        "variants": fallback_variants,
        "campaign_timeline": [
            {"label": "Teaser", "time": "Today 2PM", "type": "teaser"},
            {"label": "Speaker Bio", "time": "Tomorrow 9AM", "type": "speaker_bio"},
            {"label": "Live Update", "time": "Day of Event", "type": "live_update"},
        ],
        "reasoning": (
            "> Analyzed campaign brief and target platforms.\n"
            "> Created platform-specific content with appropriate tone and length.\n"
            "> LinkedIn: Professional, detailed post with industry hashtags.\n"
            "> Twitter/X: Punchy, emoji-rich hook with urgency.\n"
            "> Recommended 3-phase campaign: Teaser → Bio → Live Update."
        )
    }

    result = await call_llm_json(prompt, fallback)

    # Parse result into typed objects
    variants = []
    for i, v in enumerate(result.get("variants", fallback["variants"])):
        variants.append(ContentPiece(
            id=i + 1,
            platform=v.get("platform", "linkedin"),
            tone=v.get("tone", tone),
            text=v.get("text", ""),
            image_prompt=v.get("image_prompt", ""),
            status="draft",
            is_recommended=v.get("is_recommended", i == 0)
        ))

    timeline = []
    for i, t in enumerate(result.get("campaign_timeline", fallback["campaign_timeline"])):
        timeline.append(ContentQueueItem(
            id=i + 1,
            label=t.get("label", ""),
            time=t.get("time", ""),
            type=t.get("type", "teaser")
        ))

    return GenerateResult(
        variants=variants,
        campaign_timeline=timeline,
        reasoning=result.get("reasoning", fallback["reasoning"])
    )
