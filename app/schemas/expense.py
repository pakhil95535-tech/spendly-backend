from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExpenseCreate(BaseModel):
    local_id: Optional[str] = None
    amount: float
    category: str
    note: str = ""
    date: str
    time: str = ""
    payment_method: Optional[str] = "UPI"

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    note: Optional[str] = None
    date: Optional[str] = None
    payment_method: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    local_id: Optional[str]
    amount: float
    category: str
    note: str
    date: str
    time: str
    payment_method: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class BulkSyncRequest(BaseModel):
    expenses: List[ExpenseCreate]

class BulkSyncResponse(BaseModel):
    synced: int
    skipped: int

class BudgetCreate(BaseModel):
    monthly_limit: float
    month_key: str

class BudgetResponse(BaseModel):
    id: int
    monthly_limit: float
    month_key: str

    model_config = {"from_attributes": True}

class BudgetSummary(BaseModel):
    monthly_limit: float
    total_spent: float
    remaining: float
    percentage_used: float
    month_key: str