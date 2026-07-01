from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PileToggle(BaseModel):
    pile_id: int
    action: str  # START or STOP


class PileStatusResponse(BaseModel):
    id: int
    name: str
    pile_type: str
    power: float
    status: str
    accum_charge_count: int
    accum_duration: float
    accum_kwh: float
    queue_size: int = 0
    current_session_user: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleInfo(BaseModel):
    user_id: int
    username: str
    battery_capacity: Optional[float]
    requested_kwh: float
    queue_code: str
    waiting_since: datetime

    class Config:
        from_attributes = True
