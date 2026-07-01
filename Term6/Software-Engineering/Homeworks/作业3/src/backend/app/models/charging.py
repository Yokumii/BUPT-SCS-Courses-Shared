import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChargingMode(str, enum.Enum):
    FAST = "FAST"
    TRICKLE = "TRICKLE"


class RequestStatus(str, enum.Enum):
    WAITING = "WAITING"
    QUEUED = "QUEUED"
    CHARGING = "CHARGING"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"


class SessionStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    ENDED = "ENDED"


class ChargingRequest(Base):
    __tablename__ = "charging_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    mode: Mapped[ChargingMode] = mapped_column(Enum(ChargingMode), nullable=False)
    kwh: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.WAITING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    customer: Mapped["User"] = relationship(back_populates="charging_requests", foreign_keys=[user_id])
    queue_number: Mapped[Optional["QueueNumber"]] = relationship(back_populates="request", uselist=False)
    session: Mapped[Optional["ChargingSession"]] = relationship(back_populates="request", uselist=False)


class QueueNumber(Base):
    __tablename__ = "queue_numbers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    mode: Mapped[ChargingMode] = mapped_column(Enum(ChargingMode), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("charging_requests.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    request: Mapped["ChargingRequest"] = relationship(back_populates="queue_number")


class QueueSequence(Base):
    __tablename__ = "queue_sequences"
    __table_args__ = (UniqueConstraint("mode", name="uq_queue_sequence_mode"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mode: Mapped[ChargingMode] = mapped_column(Enum(ChargingMode), nullable=False)
    next_seq: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pile_id: Mapped[int] = mapped_column(Integer, ForeignKey("charging_piles.id"), nullable=False)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("charging_requests.id"), unique=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.RUNNING)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    charged_kwh: Mapped[float] = mapped_column(Float, default=0.0)
    charged_hours: Mapped[float] = mapped_column(Float, default=0.0)

    request: Mapped["ChargingRequest"] = relationship(back_populates="session")
    pile: Mapped["ChargingPile"] = relationship(back_populates="sessions")
    bill: Mapped[Optional["BillDetail"]] = relationship(back_populates="session", uselist=False)


from app.models.user import User  # noqa: E402, F401
from app.models.pile import ChargingPile  # noqa: E402, F401
from app.models.billing import BillDetail  # noqa: E402, F401
