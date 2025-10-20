from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Annotated, Optional
from datetime import datetime
from src.database.database import Base
from sqlalchemy.dialects.postgresql import TIMESTAMP

int_pk = Annotated[int, mapped_column(primary_key=True)]
str_255 = Annotated[str, mapped_column(String(255))]

class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id: Mapped[int_pk]
    user_id: Mapped[int]
    category: Mapped[Optional[str_255]]
    description: Mapped[str_255]
    amount: Mapped[int]
    raw_text: Mapped[str_255]
    transaction_dttm: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    updated_dttm: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        )


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str_255]
    pass_hash: Mapped[str_255]
