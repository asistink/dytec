from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum, String
from enum import Enum
from server.utils.database import db


class SubtestType(str, Enum):
  DOT = "dot"
  STROOP = "stroop"
  ADD = "add"
  SUBS = "subs"
  MULT = "mult"


class Question(db.Model):
  __tablename__ = "questions"

  id: Mapped[int] = mapped_column(primary_key=True)

  subtest: Mapped[SubtestType] = mapped_column(SQLEnum(SubtestType), nullable=False)

  # DOT
  dot_amount: Mapped[int | None] = mapped_column(nullable=True)

  # MATH
  left: Mapped[int | None] = mapped_column(nullable=True)
  right: Mapped[int | None] = mapped_column(nullable=True)
  operation: Mapped[str | None] = mapped_column(String(5), nullable=True)

  # STROOP
  left_value: Mapped[str | None] = mapped_column(nullable=True)
  left_font_size: Mapped[int | None] = mapped_column(nullable=True)
  right_value: Mapped[str | None] = mapped_column(nullable=True)
  right_font_size: Mapped[int | None] = mapped_column(nullable=True)

  # Answer
  correct_answer: Mapped[str] = mapped_column(nullable=False)

  choice_1: Mapped[str] = mapped_column(nullable=False)
  choice_2: Mapped[str] = mapped_column(nullable=False)
  choice_3: Mapped[str] = mapped_column(nullable=False)
  choice_4: Mapped[str] = mapped_column(nullable=False)
