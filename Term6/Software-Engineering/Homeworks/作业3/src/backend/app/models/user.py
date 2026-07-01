import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ADMINISTRATOR = "ADMINISTRATOR"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Customer-specific fields
    vehicle_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    battery_capacity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Administrator-specific fields
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    charging_requests: Mapped[List["ChargingRequest"]] = relationship(
        back_populates="customer", foreign_keys="ChargingRequest.user_id"
    )


from app.models.charging import ChargingRequest  # noqa: E402, F401
