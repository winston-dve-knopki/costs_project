from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class BaseModelAttr(BaseModel):
    pass
    class Config:
        from_attributes = True

class CostCreate(BaseModelAttr):
    description: str
    category: Optional[str]
    amount: int
    raw_text: Optional[str] = None
    transaction_dttm: datetime


class CostRead(BaseModelAttr):
    transaction_id: int
    user_id: int
    description: str
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
