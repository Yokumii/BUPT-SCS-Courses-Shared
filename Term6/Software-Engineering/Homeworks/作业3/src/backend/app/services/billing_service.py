
from datetime import datetime, time, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models.charging import ChargingSession
from app.models.billing import BillDetail, TimeWindow
from app.repositories.bill_repo import BillRepo
from app.repositories.pile_repo import PileRepo
from app.repositories.user_repo import UserRepo


class BillingService:

    def create_bill(self, session: ChargingSession, db: Session) -> BillDetail:
        bill_repo = BillRepo(db)
        existing = bill_repo.find_by_session(session.id)
        if existing:
            return existing

        start = session.start_time
        end = session.end_time or datetime.now()
        charged_kwh = session.charged_kwh
        duration_hours = (end - start).total_seconds() / 3600

        charge_fee = self.compute_charge_fee(charged_kwh, start, end)
        service_fee = round(settings.SERVICE_RATE * charged_kwh, 2)
        total_fee = round(charge_fee + service_fee, 2)

        bill = BillDetail(
            session_id=session.id,
            user_id=session.user_id,
            pile_id=session.pile_id,
            charged_kwh=round(charged_kwh, 4),
            duration=round(duration_hours, 4),
            start_time=start,
            end_time=end,
            charge_fee=charge_fee,
            service_fee=service_fee,
            total_fee=total_fee,
            created_at=datetime.now(),
        )
        bill = bill_repo.save(bill)
        UserRepo(db).deduct_balance(session.user_id, total_fee)
        return bill

    def compute_total_fee(self, kwh: float, start: datetime, end: datetime) -> float:
        charge_fee = self.compute_charge_fee(kwh, start, end)
        service_fee = round(settings.SERVICE_RATE * kwh, 2)
        return round(charge_fee + service_fee, 2)

    def compute_charge_fee(self, kwh: float, start: datetime, end: datetime) -> float:
        if kwh <= 0:
            return 0.0

        duration_hours = (end - start).total_seconds() / 3600
        if duration_hours <= 0:
            return 0.0

        power = kwh / duration_hours
        total_fee = 0.0
        current = start

        while current < end:
            next_boundary = self._next_period_boundary(current)
            segment_end = min(next_boundary, end)
            segment_hours = (segment_end - current).total_seconds() / 3600
            segment_kwh = power * segment_hours
            rate = self._get_rate_at(current)
            total_fee += segment_kwh * rate
            current = segment_end

        return round(total_fee, 2)

    def _get_rate_at(self, dt: datetime) -> float:
        t = dt.time()
        if (time(10, 0) <= t < time(15, 0)) or (time(18, 0) <= t < time(21, 0)):
            return settings.PEAK_RATE
        if t >= time(23, 0) or t < time(7, 0):
            return settings.VALLEY_RATE
        return settings.NORMAL_RATE

    def _next_period_boundary(self, dt: datetime) -> datetime:
        boundaries = [
            time(7, 0), time(10, 0), time(15, 0),
            time(18, 0), time(21, 0), time(23, 0),
        ]
        current_time = dt.time()
        for b in boundaries:
            if current_time < b:
                return dt.replace(hour=b.hour, minute=b.minute, second=0, microsecond=0)
        next_day = dt + timedelta(days=1)
        return next_day.replace(hour=7, minute=0, second=0, microsecond=0)

    def view_bills(self, user_id: int, db: Session) -> list[dict]:
        pile_repo = PileRepo(db)
        bill_repo = BillRepo(db)
        bills = bill_repo.find_by_user(user_id)
        result = []
        for b in bills:
            pile = pile_repo.find_by_id(b.pile_id)
            result.append({
                "id": b.id,
                "pile_id": b.pile_id,
                "pile_name": pile.name if pile else "",
                "charged_kwh": round(b.charged_kwh, 4),
                "duration": round(b.duration, 4),
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
                "charge_fee": b.charge_fee,
                "service_fee": b.service_fee,
                "total_fee": b.total_fee,
                "created_at": b.created_at.isoformat(),
            })
        return result

    def view_report(self, time_window: str, pile_id: Optional[int], db: Session) -> dict:
        bill_repo = BillRepo(db)
        pile_repo = PileRepo(db)
        tw = TimeWindow(time_window)
        bills = bill_repo.query_by_period(tw, pile_id)
        piles = [pile_repo.find_by_id(pile_id)] if pile_id else pile_repo.find_all()
        piles = [p for p in piles if p]

        rows = []
        for pile in piles:
            pile_bills = [b for b in bills if b.pile_id == pile.id]
            row = {
                "time_window": time_window,
                "pile_id": pile.id,
                "pile_name": pile.name,
                "total_charge_count": len(pile_bills),
                "total_duration": round(sum(b.duration for b in pile_bills), 2),
                "total_kwh": round(sum(b.charged_kwh for b in pile_bills), 2),
                "total_charge_fee": round(sum(b.charge_fee for b in pile_bills), 2),
                "total_service_fee": round(sum(b.service_fee for b in pile_bills), 2),
                "total_fee": round(sum(b.total_fee for b in pile_bills), 2),
            }
            rows.append(row)

        summary = {
            "total_charge_count": sum(r["total_charge_count"] for r in rows),
            "total_duration": round(sum(r["total_duration"] for r in rows), 2),
            "total_kwh": round(sum(r["total_kwh"] for r in rows), 2),
            "total_charge_fee": round(sum(r["total_charge_fee"] for r in rows), 2),
            "total_service_fee": round(sum(r["total_service_fee"] for r in rows), 2),
            "total_fee": round(sum(r["total_fee"] for r in rows), 2),
        }

        return {
            "time_window": time_window,
            "pile_id": pile_id,
            "rows": rows,
            "summary": summary,
        }
