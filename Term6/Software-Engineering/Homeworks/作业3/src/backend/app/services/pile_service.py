
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.pile import PileStatus
from app.models.charging import ChargingSession, SessionStatus, RequestStatus, ChargingMode
from app.repositories.pile_repo import PileRepo
from app.repositories.request_repo import RequestRepo
from app.services.scheduler import scheduler
from app.services.session_service import session_service


class PileService:

    def end_charging(self, user_id: int, db: Session) -> dict:
        req_repo = RequestRepo(db)
        pile_repo = PileRepo(db)

        active = req_repo.find_active_by_user(user_id)
        if not active or active.status != RequestStatus.CHARGING:
            raise ValueError("当前未在充电中")

        session = db.query(ChargingSession).filter(
            ChargingSession.request_id == active.id,
            ChargingSession.status == SessionStatus.RUNNING
        ).first()
        if not session:
            raise ValueError("找不到活跃充电会话")

        pile = pile_repo.find_by_id(session.pile_id)
        bill = session_service.finalize_session(session, pile, db)

        scheduler.on_charging_complete(session.pile_id, db)
        scheduler.try_dispatch(db)

        return {
            "bill_id": bill.id,
            "charged_kwh": bill.charged_kwh,
            "duration": bill.duration,
            "charge_fee": bill.charge_fee,
            "service_fee": bill.service_fee,
            "total_fee": bill.total_fee,
        }

    def toggle_pile(self, pile_id: int, action: str, db: Session) -> dict:
        pile_repo = PileRepo(db)
        req_repo = RequestRepo(db)
        pile = pile_repo.find_by_id(pile_id)
        if not pile:
            raise ValueError("充电桩不存在")

        if action == "START":
            if pile.status == PileStatus.ONLINE:
                raise ValueError("充电桩已在运行中")
            pile.status = PileStatus.ONLINE
            pile.last_started_at = datetime.now()
            pile_repo.update(pile)
            pq = scheduler.pile_queues.get(pile_id)
            if pq:
                pq.status = PileStatus.ONLINE
            scheduler.on_pile_recovered(pile_id, db)
        elif action == "STOP":
            if pile.status == PileStatus.OFFLINE:
                raise ValueError("充电桩已停止")
            active_session = pile_repo.find_active_session(pile_id)
            if active_session:
                session_service.finalize_session(active_session, pile, db)

            pq = scheduler.pile_queues.get(pile_id)
            displaced = []
            if pq:
                displaced = list(pq.entries[1:] if active_session else pq.entries)
                pq.entries.clear()
                pq.status = PileStatus.OFFLINE

            for entry in sorted(displaced, key=lambda e: e.queue_seq, reverse=True):
                if entry.mode == ChargingMode.FAST:
                    scheduler.waiting_queue.fast_list.insert(0, entry)
                else:
                    scheduler.waiting_queue.trickle_list.insert(0, entry)
                req = req_repo.find_by_id(entry.request_id)
                if req:
                    req.status = RequestStatus.WAITING
                    req_repo.update(req)

            pile.status = PileStatus.OFFLINE
            pile.last_stopped_at = datetime.now()
            pile_repo.update(pile)
            scheduler.try_dispatch(db)
        else:
            raise ValueError("action 必须为 START 或 STOP")

        return {"pile_id": pile_id, "status": pile.status.value}

    def view_all_pile_status(self, db: Session) -> list[dict]:
        from app.repositories.user_repo import UserRepo

        pile_repo = PileRepo(db)
        user_repo = UserRepo(db)
        req_repo = RequestRepo(db)
        piles = pile_repo.find_all()
        result = []
        for pile in piles:
            pq = scheduler.pile_queues.get(pile.id)
            queue_size = max(len(pq.entries) - 1, 0) if pq else 0
            current_entry = pq.entries[0] if pq and pq.entries else None
            current_user = user_repo.find_by_id(current_entry.user_id) if current_entry else None
            current_req = req_repo.find_by_id(current_entry.request_id) if current_entry else None
            result.append({
                "id": pile.id,
                "name": pile.name,
                "pile_type": pile.pile_type.value,
                "power": pile.power,
                "status": pile.status.value,
                "accum_charge_count": pile.accum_charge_count,
                "accum_duration": round(pile.accum_duration, 2),
                "accum_kwh": round(pile.accum_kwh, 2),
                "queue_size": queue_size,
                "current_user_id": current_entry.user_id if current_entry else None,
                "current_username": current_user.username if current_user else None,
                "current_queue_code": current_entry.queue_code if current_entry else None,
                "current_requested_kwh": current_entry.kwh if current_entry else None,
                "current_battery_capacity": current_user.battery_capacity if current_user else None,
                "current_started_at": current_req.created_at.isoformat() if current_req else None,
            })
        return result

    def view_queuing_vehicles(self, pile_id: int, db: Session) -> list[dict]:
        from app.repositories.user_repo import UserRepo

        pq = scheduler.pile_queues.get(pile_id)
        if not pq:
            raise ValueError("充电桩不存在")

        user_repo = UserRepo(db)
        req_repo = RequestRepo(db)
        now = datetime.now()
        result = []
        for entry in pq.entries[1:]:
            user = user_repo.find_by_id(entry.user_id)
            req = req_repo.find_by_id(entry.request_id)
            waiting_minutes = 0
            if req:
                waiting_minutes = max(int((now - req.created_at).total_seconds() // 60), 0)
            result.append({
                "user_id": entry.user_id,
                "username": user.username if user else "",
                "battery_capacity": user.battery_capacity if user else None,
                "requested_kwh": entry.kwh,
                "queue_code": entry.queue_code,
                "waiting_since": req.created_at.isoformat() if req else "",
                "waiting_minutes": waiting_minutes,
                "waiting_duration": self._format_waiting_duration(waiting_minutes),
            })
        return result

    def _format_waiting_duration(self, minutes: int) -> str:
        hours = minutes // 60
        mins = minutes % 60
        if hours:
            return f"{hours}小时{mins}分钟"
        return f"{mins}分钟"
