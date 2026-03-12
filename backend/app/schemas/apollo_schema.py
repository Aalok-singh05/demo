from pydantic import BaseModel
from typing import List, Optional


class ContentRequest(BaseModel):

    action: str

    event_description: str

    target_audience: Optional[str] = None

    tone: Optional[str] = None

    platform: Optional[str] = None

    historical_data: Optional[str] = None

    existing_content_id: Optional[str] = None


class ContentPiece(BaseModel):

    platform: str
    text: str
    suggested_time: str


class ContentResult(BaseModel):

    content_pieces: List[ContentPiece]

    campaign_timeline: Optional[List[str]]

    engagement_insights: Optional[str]

    reasoning: str