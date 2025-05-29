from typing import Annotated

from sqlalchemy import Integer, MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from typing import Annotated
from sqlalchemy import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from uuid import UUID
import datetime


intpk = Annotated[int, mapped_column(
    primary_key=True, index=True, autoincrement=True)]


class Base(DeclarativeBase):
    __abstract__ = True
    type_annotation_map = {
        intpk: Integer
    }
    id: Mapped[int] = mapped_column(
        unique=True, primary_key=True, autoincrement=True)


class UserHistory(Base):
    __tablename__ = 'users_histories'
    uuid: Mapped[UUID] = mapped_column(index=True, unique=True)
    requests_history: Mapped[dict] = mapped_column(JSONB, default=dict)


class History(Base):
    __tablename__ = 'history'
    city: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
    request_count: Mapped[int] = mapped_column()
