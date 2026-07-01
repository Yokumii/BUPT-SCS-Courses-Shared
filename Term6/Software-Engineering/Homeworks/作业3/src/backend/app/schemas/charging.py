from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChargingRequestCreate(BaseModel):
    mode: str  # FAST or TRICKLE
    kwh: float


class ChargingModeModify(BaseModel):
    new_mode: str  # FAST or TRICKLE


class ChargingAmountModify(BaseModel):
    new_kwh: float


class QueueNumberResponse(BaseModel):
    code: str
    mode: str
    seq: int
    status: str
    position: Optional[int] = None

    class Config:
        from_attributes = True


class WaitingCountResponse(BaseModel):
    waiting_count: int
    mode: str


class ChargingRequestResponse(BaseModel):
    id: int
    mode: str
    kwh: float
    status: str
    queue_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
