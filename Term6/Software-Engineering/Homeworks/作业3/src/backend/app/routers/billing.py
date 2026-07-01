from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_dependencies import require_admin, require_customer
from app.services.billing_service import BillingService
from app.services.session_service import session_service

router = APIRouter(prefix="/api/billing", tags=["billing"])
billing_service = BillingService()


def reconcile(db: Session):
    session_service.auto_complete_due_sessions(db)


@router.get("/bills")
def view_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    reconcile(db)
    return billing_service.view_bills(current_user.id, db)


@router.get("/report")
def view_report(
    time_window: str,
    pile_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        reconcile(db)
        return billing_service.view_report(time_window, pile_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
