from pydantic import BaseModel
from typing import Dict, Optional

class InsightRequest(BaseModel):
    month_total: float
    today_total: float
    budget: Optional[float] = None
    category_breakdown: Dict[str, float] = {}

class InsightResponse(BaseModel):
    insights: str