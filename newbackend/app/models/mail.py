# Mail-related Pydantic models

from pydantic import BaseModel
from typing import Optional, List, Literal


class EmailPreview(BaseModel):
    """Preview of a personalized email."""
    to: str
    subject: str
    body: str


class MailRequest(BaseModel):
    """Input to the Mail Agent (Hermes)."""
    action: Literal["parse_data", "personalize", "segment", "send"]
    data_file: Optional[str] = None
    base_template: Optional[str] = None
    segment_criteria: Optional[str] = None
    recipients: Optional[List[dict]] = None


class MailResult(BaseModel):
    """Output from the Mail Agent."""
    action_completed: str
    participants_processed: int = 0
    invalid_emails: List[dict] = []
    segments_created: List[dict] = []
    preview_emails: List[EmailPreview] = []
    ready_to_send: bool = False
    requires_approval: bool = True
    reasoning: str = ""
