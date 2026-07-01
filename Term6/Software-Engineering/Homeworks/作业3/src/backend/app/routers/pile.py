from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.pile import PileToggle
from app.services.auth_dependencies import require_admin, require_customer
from app.services.pile_service import PileService
from app.services.scheduler import scheduler
from app.services.fault_monitor import fault_monitor
from app.services.session_service import session_service
from app.models.billing import SchedulingMode
from app.repositories.bill_repo import BillRepo

router = APIRouter(prefix="/api/pile", tags=["pile"])
pile_service = PileService()


def reconcile(db: Session):
    session_service.auto_complete_due_sessions(db)


@router.post("/end-charging")
def end_charging(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        reconcile(db)
        return pile_service.end_charging(current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/toggle")
def toggle_pile(
    data: PileToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        reconcile(db)
        return pile_service.toggle_pile(data.pile_id, data.action, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
def view_all_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    reconcile(db)
    return pile_service.view_all_pile_status(db)


@router.get("/queuing/{pile_id}")
def view_queuing_vehicles(
    pile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        reconcile(db)
        return pile_service.view_queuing_vehicles(pile_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/scheduling-policy")
def set_scheduling_policy(
    mode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        reconcile(db)
        scheduling_mode = SchedulingMode(mode)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的调度模式，可选: BASELINE, MIN_SINGLE, MIN_BATCH")

    scheduler.set_policy(scheduling_mode)
    BillRepo(db).update_scheduling_policy(scheduling_mode, current_user.id)
    return {"mode": mode, "message": "调度策略已切换"}


@router.post("/fault/{pile_id}")
def report_fault(
    pile_id: int,
    strategy: str = "PRIORITY",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    reconcile(db)
    result = fault_monitor.handle_fault(pile_id, db, strategy=strategy)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/recover/{pile_id}")
def report_recovery(
    pile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    reconcile(db)
    result = fault_monitor.handle_recovery(pile_id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
