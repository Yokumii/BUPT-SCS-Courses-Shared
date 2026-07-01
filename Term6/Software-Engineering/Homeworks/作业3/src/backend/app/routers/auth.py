from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserInfo, VehicleUpdate, RechargeRequest
from app.services.auth_dependencies import get_current_user, require_customer
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])
user_service = UserService()


@router.post("/register", response_model=dict)
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        user = user_service.register(data.username, data.password, data.phone, db)
        return {"user_id": user.id, "username": user.username, "message": "注册成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        return user_service.login(data.username, data.password, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        phone=current_user.phone,
        role=current_user.role.value,
        vehicle_id=current_user.vehicle_id,
        battery_capacity=current_user.battery_capacity,
        balance=current_user.balance or 0.0,
        created_at=current_user.created_at,
    )


@router.put("/vehicle")
def update_vehicle(
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    user = user_service.update_vehicle(current_user.id, data.vehicle_id, data.battery_capacity, db)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "车辆信息更新成功"}


@router.post("/recharge")
def recharge(
    data: RechargeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        user = user_service.recharge(current_user.id, data.amount, db)
        return {"balance": user.balance, "message": "充值成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
