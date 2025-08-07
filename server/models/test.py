from server.utils.database import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import DateTime

if TYPE_CHECKING:
  from server.models.user import User


class Test(db.Model):
  __tablename__ = "tests"

  id: Mapped[int] = mapped_column(primary_key=True)

  srt: Mapped[float]

  dot_rt: Mapped[float]
  dot_acc: Mapped[float]
  dot_stanine: Mapped[float]

  stroop_rt: Mapped[float]
  stroop_acc: Mapped[float]
  stroop_stanine: Mapped[float]

  add_rt: Mapped[float]
  add_acc: Mapped[float]
  add_stanine: Mapped[float]

  subs_rt: Mapped[float]
  subs_acc: Mapped[float]
  subs_stanine: Mapped[float]

  mult_rt: Mapped[float]
  mult_acc: Mapped[float]
  mult_stanine: Mapped[float]

  label: Mapped[int]
  dysc_prob: Mapped[float]

  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  user: Mapped["User"] = relationship("User", back_populates="tests")

  created_at: Mapped[datetime] = mapped_column(
    DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
  )

  updated_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
    nullable=False,
  )

  def to_simple_dict(self):
    return {
      "id": self.id,
      "user_id": self.user_id,
      "label": self.label,
      "created_at": self.created_at.isoformat(),
      "updated_at": self.updated_at.isoformat(),
    }

  def to_dict(self):
    return {
      "id": self.id,
      "user_id": self.user_id,
      "dot_stanine": self.dot_stanine,
      "stroop_stanine": self.stroop_stanine,
      "add_stanine": self.add_stanine,
      "mult_stanine": self.mult_stanine,
      "subs_stanine": self.subs_stanine,
      "label": self.label,
      "dysc_prob": self.dysc_prob,
      "created_at": self.created_at.isoformat(),
      "updated_at": self.updated_at.isoformat(),
    }
