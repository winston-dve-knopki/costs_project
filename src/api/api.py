import json
import src.common.schemas as schemas
from src.database.models import Transaction, TransactionType
from fastapi import APIRouter, Depends, Query, status, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
import src.database.models as models
from src.database.database import get_session
from datetime import datetime, date, timedelta
from sqlalchemy import select, delete
from typing import List, Optional, Any


router = APIRouter()

@router.post("/transaction", response_model=schemas.CostRead)
async def create_transaction(
    cost_data: schemas.CostCreate, 
    session: AsyncSession = Depends(get_session)
):
    user_id = 1

    cur_dttm = datetime.now()

    db_cost = models.Transaction(
        **cost_data.model_dump(),
        user_id=user_id
    )

    session.add(db_cost)

    await session.commit()
    await session.refresh(db_cost)
    return db_cost

@router.get("/transactions", response_model=List[schemas.CostRead])
async def read_transactions(
    limit: int = Query(1000, gt=0),
    sort: str = Query("transaction_id", description="Field to sort by"),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    user_id: int = Query(1),
    amount: int = Query(0),
    transaction_type: TransactionType | None = None,
    category: str | None = None,
    session: AsyncSession = Depends(get_session)
    ):

    if date_from is None:
        date_from = datetime.now() - timedelta(days=7)
    if date_to is None:
        date_to = datetime.now()
    
    allowed_columns = ["transaction_id", "transaction_dttm", "amount"]
    if sort not in allowed_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort column. Allowed: {', '.join(allowed_columns)}"
        )
    query = select(Transaction).where(
        Transaction.transaction_dttm >= date_from,
        Transaction.transaction_dttm <= date_to,
        Transaction.user_id == user_id,
        Transaction.amount > amount,
    ).order_by(sort).limit(limit)
    if category:
        query = query.where(Transaction.category == category)
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
    result = await session.execute(query)
    result_lst = result.scalars().all()
    print(result_lst)
    return result_lst

@router.delete("/transactions", response_model=List[schemas.CostRead])
async def delete_transactions(
    ids_json: str = Query(..., alias="ids_to_delete"),  # Fixed parameter declaration
    session: AsyncSession = Depends(get_session)
):
    try:
        ids_to_delete = json.loads(ids_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    select_stmt = select(Transaction).where(Transaction.transaction_id.in_(ids_to_delete))
    result = await session.execute(select_stmt)
    transactions = result.scalars().all()

    query = delete(Transaction).where(Transaction.transaction_id.in_(ids_to_delete))
    await session.execute(query)
    await session.commit()
    return transactions
