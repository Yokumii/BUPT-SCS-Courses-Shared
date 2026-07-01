from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.billing import BillDetail, SchedulingPolicy, SchedulingMode, TimeWindow


class BillRepo:
    def __init__(self, db: Session):
        self.db = db

    def save(self, bill: BillDetail) -> BillDetail:
        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)
        return bill

    def find_by_user(self, user_id: int) -> list[BillDetail]:
        return self.db.query(BillDetail).filter(
            BillDetail.user_id == user_id
        ).order_by(BillDetail.created_at.desc()).all()

    def find_by_id(self, bill_id: int) -> Optional[BillDetail]:
        return self.db.query(BillDetail).filter(BillDetail.id == bill_id).first()

    def find_by_session(self, session_id: int) -> Optional[BillDetail]:
        return self.db.query(BillDetail).filter(BillDetail.session_id == session_id).first()

    def query_by_period(self, time_window: TimeWindow, pile_id: Optional[int] = None):
        now = datetime.now()
        if time_window == TimeWindow.DAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_window == TimeWindow.WEEK:
            start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        query = self.db.query(BillDetail).filter(BillDetail.created_at >= start)
        if pile_id:
            query = query.filter(BillDetail.pile_id == pile_id)
        return query.all()

    def get_scheduling_policy(self) -> Optional[SchedulingPolicy]:
        return self.db.query(SchedulingPolicy).order_by(SchedulingPolicy.id.desc()).first()

    def save_scheduling_policy(self, policy: SchedulingPolicy) -> SchedulingPolicy:
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy

    def update_scheduling_policy(self, mode: SchedulingMode, admin_id: int):
        policy = self.get_scheduling_policy()
        if policy:
            policy.mode = mode
            policy.activated_at = datetime.now()
            policy.activated_by = admin_id
        else:
            policy = SchedulingPolicy(mode=mode, activated_by=admin_id)
            self.db.add(policy)
        self.db.commit()
        return policy
