# Content-related Pydantic models

from pydantic import BaseModel
from typing import Optional, List, Literal


class ContentPiece(BaseModel):
    """A single content item (social post, email header, etc.)."""
    id: str = ""
    platform: str = "twitter"  # twitter, linkedin, instagram, email
    tone: str = "professional"  # professional, casual, hype
    text: str
    hashtags: List[str] = []
    suggested_time: Optional[str] = None
    image_prompt: Optional[str] = None
    status: str = "draft"


class CampaignPlan(BaseModel):
    """A multi-post campaign plan."""
    phases: List[str] = []  # Teaser, Reveal, Countdown, D-Day, Recap
    total_posts: int = 0
    duration_days: int = 7


class EngagementAnalysis(BaseModel):
    """Engagement analysis from historical data."""
    best_day: Optional[str] = None
    best_time: Optional[str] = None
    top_content_type: Optional[str] = None
    insights: List[str] = []


class ContentRequest(BaseModel):
    """Input to the Content Agent (Apollo)."""
    action: Literal["generate", "plan_campaign", "analyze_timing", "update_content"]
    event_description: str = ""
    target_audience: Optional[str] = None
    tone: Optional[str] = "auto"
    platform: Optional[str] = None
    historical_data: Optional[str] = None
    existing_content_id: Optional[str] = None


class ContentResult(BaseModel):
    """Output from the Content Agent."""
    content_pieces: List[ContentPiece] = []
    campaign_timeline: Optional[CampaignPlan] = None
    engagement_insights: Optional[EngagementAnalysis] = None
    reasoning: str = ""
