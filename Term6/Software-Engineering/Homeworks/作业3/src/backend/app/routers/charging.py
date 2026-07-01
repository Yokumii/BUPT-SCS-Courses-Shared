from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.charging import ChargingRequestCreate, ChargingModeModify, ChargingAmountModify
from app.services.auth_dependencies import require_customer
from app.services.charging_service import ChargingService
from app.services.session_service import session_service
from app.services.time_service import time_service

router = APIRouter(prefix="/api/charging", tags=["charging"])
charging_service = ChargingService()


def reconcile(db: Session):
    session_service.auto_complete_due_sessions(db)


@router.post("/submit")
def submit_charging_request(
    data: ChargingRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        reconcile(db)
        return charging_service.submit_charging_request(current_user.id, data.mode, data.kwh, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/demo/advance-time")
def advance_demo_time(
    minutes: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    if minutes not in (10, 30, 60):
        raise HTTPException(status_code=400, detail="快进时间仅支持 10、30、60 分钟")
    current_time = time_service.advance(minutes)
    bills = session_service.auto_complete_due_sessions(db)
    db.refresh(current_user)
    return {
        "current_time": current_time.isoformat(),
        "bill_ids": [b.id for b in bills],
        "generated_count": len(bills),
        "balance": current_user.balance or 0.0,
    }


@router.put("/modify-mode")
def modify_mode(
    data: ChargingModeModify,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        reconcile(db)
        return charging_service.modify_charging_mode(current_user.id, data.new_mode, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/modify-amount")
def modify_amount(
    data: ChargingAmountModify,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        reconcile(db)
        return charging_service.modify_charging_amount(current_user.id, data.new_kwh, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel")
def cancel_charging(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        reconcile(db)
        return charging_service.cancel_charging(current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/queue-number")
def view_queue_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    reconcile(db)
    result = charging_service.view_queue_number(current_user.id, db)
    if not result:
        raise HTTPException(status_code=404, detail="无活跃充电请求")
    return result


@router.get("/waiting-count")
def view_waiting_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        reconcile(db)
        return charging_service.view_waiting_count(current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
