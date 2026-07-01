from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BillDetailResponse(BaseModel):
    id: int
    pile_id: int
    pile_name: Optional[str] = None
    charged_kwh: float
    duration: float
    start_time: datetime
    end_time: datetime
    charge_fee: float
    service_fee: float
    total_fee: float
    created_at: datetime

    class Config:
        from_attributes = True


class ReportRequest(BaseModel):
    time_window: str  # DAY, WEEK, MONTH
    pile_id: Optional[int] = None


class ReportResponse(BaseModel):
    time_window: str
    pile_id: Optional[int]
    total_charge_count: int
    total_duration: float
    total_kwh: float
    total_charge_fee: float
    total_service_fee: float
    total_fee: float
