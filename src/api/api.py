import src.common.schemas as schemas
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
import src.database.models as models
from src.database.database import get_session
from datetime import datetime

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
