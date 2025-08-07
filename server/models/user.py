from server.utils.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from sqlalchemy import DateTime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from server.models.test import Test


class User(db.Model):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str]
  email: Mapped[str] = mapped_column(unique=True)
  picture: Mapped[str] = mapped_column(nullable=True)
  age: Mapped[int] = mapped_column(nullable=True)
  key: Mapped[str]

  created_at: Mapped[datetime] = mapped_column(
    DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
  )

  updated_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
    nullable=False,
  )

  tests: Mapped[list["Test"]] = relationship(
    "Test", back_populates="user", cascade="all, delete-orphan"
  )
