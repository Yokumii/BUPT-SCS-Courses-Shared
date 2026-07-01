from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    username: str
    password: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    username: str


class UserInfo(BaseModel):
    id: int
    username: str
    phone: Optional[str]
    role: str
    vehicle_id: Optional[str]
    battery_capacity: Optional[float]
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleUpdate(BaseModel):
    vehicle_id: str
    battery_capacity: float


class RechargeRequest(BaseModel):
    amount: float
