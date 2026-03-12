from pydantic import BaseModel


class AnalyticsRequest(BaseModel):

    schedule_data: dict

    participant_data: dict


class AnalyticsResult(BaseModel):

    insight: str

    priority: str

    recommended_action: str

    target_agent: str

    reasoning: str