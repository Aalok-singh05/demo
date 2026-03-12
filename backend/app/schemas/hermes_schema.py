from pydantic import BaseModel
from typing import List, Optional


class MailRequest(BaseModel):

    action: str
    data_file: Optional[str] = None
    base_template: Optional[str] = None
    segment_criteria: Optional[str] = None
    recipients: Optional[List[str]] = None


class MailResult(BaseModel):

    action_completed: str
    participants_processed: int
    invalid_emails: List[str]

    preview_emails: List[str]

    ready_to_send: bool

    reasoning: str