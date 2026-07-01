import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PileType(str, enum.Enum):
    FAST = "FAST"
    TRICKLE = "TRICKLE"


class PileStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    FAULT = "FAULT"


class ChargingPile(Base):
    __tablename__ = "charging_piles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    pile_type: Mapped[PileType] = mapped_column(Enum(PileType), nullable=False)
    power: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PileStatus] = mapped_column(Enum(PileStatus), default=PileStatus.OFFLINE)
    last_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    accum_charge_count: Mapped[int] = mapped_column(Integer, default=0)
    accum_duration: Mapped[float] = mapped_column(Float, default=0.0)
    accum_kwh: Mapped[float] = mapped_column(Float, default=0.0)

    sessions: Mapped[List["ChargingSession"]] = relationship(back_populates="pile")


from app.models.charging import ChargingSession  # noqa: E402, F401
