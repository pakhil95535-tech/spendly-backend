from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.database import get_db
from app.models.expense import Budget, Expense
from app.models.user import User
from app.schemas.expense import BudgetCreate, BudgetResponse, BudgetSummary
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/budget", tags=["Budget"])

@router.get("", response_model=Optional[BudgetResponse])
async def get_budget(
    month: str = Query(..., description="Format: 2026-04"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Budget).where(Budget.user_id == current_user.id, Budget.month_key == month)
    )
    return result.scalar_one_or_none()

@router.post("", response_model=BudgetResponse)
async def set_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Budget).where(Budget.user_id == current_user.id, Budget.month_key == data.month_key)
    )
    budget = result.scalar_one_or_none()

    if budget:
        budget.monthly_limit = data.monthly_limit
    else:
        budget = Budget(user_id=current_user.id, monthly_limit=data.monthly_limit, month_key=data.month_key)
        db.add(budget)

    await db.commit()
    await db.refresh(budget)
    return budget

@router.get("/summary", response_model=BudgetSummary)
async def get_budget_summary(
    month: str = Query(..., description="Format: 2026-04"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    budget_result = await db.execute(
        select(Budget).where(Budget.user_id == current_user.id, Budget.month_key == month)
    )
    budget = budget_result.scalar_one_or_none()
    monthly_limit = budget.monthly_limit if budget else 0

    expenses_result = await db.execute(
        select(Expense).where(Expense.user_id == current_user.id, Expense.date.like(f"{month}%"))
    )
    expenses = expenses_result.scalars().all()
    total_spent = sum(e.amount for e in expenses)
    remaining = monthly_limit - total_spent
    percentage = (total_spent / monthly_limit * 100) if monthly_limit > 0 else 0

    return BudgetSummary(
        monthly_limit=monthly_limit,
        total_spent=total_spent,
        remaining=remaining,
        percentage_used=round(percentage, 1),
        month_key=month
    )