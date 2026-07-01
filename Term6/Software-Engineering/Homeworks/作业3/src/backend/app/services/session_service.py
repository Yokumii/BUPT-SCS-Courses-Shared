from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.charging import ChargingSession, SessionStatus, RequestStatus
from app.models.pile import ChargingPile
from app.models.billing import BillDetail
from app.repositories.bill_repo import BillRepo
from app.repositories.user_repo import UserRepo
from app.services.billing_service import BillingService
from app.services.time_service import time_service


class SessionService:

    def finalize_session(
        self,
        session: ChargingSession,
        pile: ChargingPile,
        db: Session,
        end_time: Optional[datetime] = None,
        request_status: RequestStatus = RequestStatus.ENDED,
    ) -> BillDetail:
        if session.bill:
            return session.bill

        end = end_time or time_service.now()
        if end < session.start_time:
            end = session.start_time

        duration_hours = (end - session.start_time).total_seconds() / 3600
        requested_kwh = session.request.kwh if session.request else 0
        charged_kwh = min(duration_hours * pile.power, requested_kwh)
        if requested_kwh and abs(charged_kwh - requested_kwh) < 1e-6:
            charged_kwh = requested_kwh

        session.status = SessionStatus.ENDED
        session.end_time = end
        session.charged_kwh = charged_kwh
        session.charged_hours = duration_hours
        if session.request:
            session.request.status = request_status
        db.commit()

        bill = BillingService().create_bill(session, db)

        pile.accum_charge_count += 1
        pile.accum_duration += duration_hours
        pile.accum_kwh += charged_kwh
        db.commit()
        db.refresh(bill)
        return bill

    def auto_complete_due_sessions(self, db: Session) -> list[BillDetail]:
        from app.models.charging import ChargingSession
        from app.repositories.pile_repo import PileRepo
        from app.services.scheduler import scheduler

        now = time_service.now()
        pile_repo = PileRepo(db)
        sessions = db.query(ChargingSession).filter(
            ChargingSession.status == SessionStatus.RUNNING
        ).all()
        bills: list[BillDetail] = []

        for session in sessions:
            pile = pile_repo.find_by_id(session.pile_id)
            req = session.request
            user = UserRepo(db).find_by_id(session.user_id)
            if not pile or not req or not user or pile.power <= 0:
                continue

            required_hours = req.kwh / pile.power
            due_at = session.start_time + timedelta(hours=required_hours)
            check_until = min(now, due_at)
            finish_at = None

            if user.balance is not None and user.balance > 0 and check_until > session.start_time:
                fee_now = self._fee_at(pile, req.kwh, session.start_time, check_until)
                if fee_now >= user.balance:
                    finish_at = self._find_balance_exhaust_time(
                        pile, req.kwh, session.start_time, check_until, user.balance
                    )
            elif user.balance is not None and user.balance <= 0 and check_until > session.start_time:
                finish_at = session.start_time

            if finish_at is None and now >= due_at:
                finish_at = due_at

            if finish_at is not None:
                bill = self.finalize_session(session, pile, db, end_time=finish_at)
                bills.append(bill)
                scheduler.on_charging_complete(session.pile_id, db)

        if bills:
            scheduler.try_dispatch(db)
        return bills

    def _fee_at(self, pile: ChargingPile, requested_kwh: float, start: datetime, end: datetime) -> float:
        duration_hours = max((end - start).total_seconds() / 3600, 0)
        charged_kwh = min(duration_hours * pile.power, requested_kwh)
        return BillingService().compute_total_fee(charged_kwh, start, end)

    def _find_balance_exhaust_time(
        self, pile: ChargingPile, requested_kwh: float, start: datetime, end: datetime, balance: float
    ) -> datetime:
        low = start
        high = end
        for _ in range(24):
            mid = low + (high - low) / 2
            if self._fee_at(pile, requested_kwh, start, mid) >= balance:
                high = mid
            else:
                low = mid
        return high


session_service = SessionService()
