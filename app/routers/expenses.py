from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from app.database import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, BulkSyncRequest, BulkSyncResponse
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("", response_model=List[ExpenseResponse])
async def get_expenses(
    month: Optional[str] = Query(None, description="Format: 2026-04"),
    date: Optional[str] = Query(None, description="Format: 2026-04-12"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Expense).where(Expense.user_id == current_user.id)
    if date:
        query = query.where(Expense.date == date)
    elif month:
        query = query.where(Expense.date.like(f"{month}%"))
    query = query.order_by(Expense.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    expense = Expense(
        user_id=current_user.id,
        local_id=data.local_id,
        amount=data.amount,
        category=data.category,
        note=data.note,
        date=data.date,
        time=data.time,
        payment_method=data.payment_method,
        is_synced=True
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense

@router.post("/bulk-sync", response_model=BulkSyncResponse)
async def bulk_sync(
    data: BulkSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    synced, skipped = 0, 0
    for exp_data in data.expenses:
        # Check if already synced using local_id
        if exp_data.local_id:
            existing = await db.execute(
                select(Expense).where(
                    Expense.user_id == current_user.id,
                    Expense.local_id == exp_data.local_id
                )
            )
            if existing.scalar_one_or_none():
                skipped += 1
                continue

        expense = Expense(
            user_id=current_user.id,
            local_id=exp_data.local_id,
            amount=exp_data.amount,
            category=exp_data.category,
            note=exp_data.note,
            date=exp_data.date,
            time=exp_data.time,
            payment_method=exp_data.payment_method,
            is_synced=True
        )
        db.add(expense)
        synced += 1

    await db.commit()
    return BulkSyncResponse(synced=synced, skipped=skipped)

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(expense, field, value)

    await db.commit()
    await db.refresh(expense)
    return expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id)
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await db.delete(expense)
    await db.commit()