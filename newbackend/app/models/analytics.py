# Analytics-related Pydantic models

from pydantic import BaseModel
from typing import Optional, List


class InsightItem(BaseModel):
    """A single analytics insight."""
    type: str  # registration_trend, capacity_warning, demographic, etc.
    icon: str = "📊"
    message: str
    severity: str = "info"  # info, warning, critical


class RiskItem(BaseModel):
    """A detected risk."""
    risk: str
    severity: str = "medium"  # low, medium, high
    recommendation: str = ""


class CapacityWarning(BaseModel):
    """A capacity mismatch warning."""
    session_title: str
    venue: str
    registrants: int
    capacity: int
    recommendation: str = ""


class AnalyticsResult(BaseModel):
    """Output from the Analytics Agent (Athena)."""
    insights: List[InsightItem] = []
    risk_items: List[RiskItem] = []
    capacity_warnings: List[CapacityWarning] = []
    metrics: dict = {}
    reasoning: str = ""
