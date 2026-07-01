import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TimeWindow(str, enum.Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class SchedulingMode(str, enum.Enum):
    BASELINE = "BASELINE"
    MIN_SINGLE = "MIN_SINGLE"
    MIN_BATCH = "MIN_BATCH"


class BillDetail(Base):
    __tablename__ = "bill_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("charging_sessions.id"), unique=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    pile_id: Mapped[int] = mapped_column(Integer, ForeignKey("charging_piles.id"), nullable=False)
    charged_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    charge_fee: Mapped[float] = mapped_column(Float, nullable=False)
    service_fee: Mapped[float] = mapped_column(Float, nullable=False)
    total_fee: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    session: Mapped["ChargingSession"] = relationship(back_populates="bill")


class SchedulingPolicy(Base):
    __tablename__ = "scheduling_policy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mode: Mapped[SchedulingMode] = mapped_column(Enum(SchedulingMode), default=SchedulingMode.BASELINE)
    activated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    activated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)


from app.models.charging import ChargingSession  # noqa: E402, F401
