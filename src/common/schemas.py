from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
from src.database.models import TransactionType

class BaseModelAttr(BaseModel):
    pass
    class Config:
        from_attributes = True

class CostCreate(BaseModelAttr):
    description: str
    category: Optional[str]
    amount: int
    transaction_type: TransactionType
    raw_text: Optional[str] = None
    transaction_dttm: datetime


class CostRead(BaseModelAttr):
    model_config = ConfigDict(from_attributes=True)
    transaction_id: int
    user_id: int
    description: str
    transaction_type: TransactionType
    category: Optional[str]
    amount: int
    raw_text: Optional[str] = None
    transaction_dttm: datetime
    updated_dttm: datetime


class UserCreate(BaseModelAttr):
    user: str
    pas: str


class UserRead(BaseModelAttr):
    user: str
    pass_hash: str
