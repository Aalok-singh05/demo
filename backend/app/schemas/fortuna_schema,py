from pydantic import BaseModel


class BudgetRequest(BaseModel):

    venue_costs: dict

    speaker_costs: dict

    schedule: dict


class BudgetResult(BaseModel):

    total_cost: float

    warnings: list

    recommended_action: str

    reasoning: str