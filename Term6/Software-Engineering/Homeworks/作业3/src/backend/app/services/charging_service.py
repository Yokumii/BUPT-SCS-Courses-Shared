
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.charging import ChargingRequest, QueueNumber, ChargingMode, RequestStatus, ChargingSession, SessionStatus
from app.repositories.request_repo import RequestRepo
from app.repositories.pile_repo import PileRepo
from app.repositories.user_repo import UserRepo
from app.services.scheduler import scheduler, PileQueueEntry
from app.services.session_service import session_service


class ChargingService:

    def submit_charging_request(
        self, user_id: int, mode: str, kwh: float, db: Session
    ) -> dict:
        req_repo = RequestRepo(db)
        user = UserRepo(db).find_by_id(user_id)
        if not user or (user.balance or 0.0) <= 0:
            raise ValueError("账户余额不足，请先充值")

        active = req_repo.find_active_by_user(user_id)
        if active:
            raise ValueError("当前已有活跃充电请求，请先完成或取消")

        if scheduler.waiting_queue.is_full():
            raise ValueError("等候区已满，请稍后再试")

        charging_mode = ChargingMode(mode)

        request = ChargingRequest(
            user_id=user_id,
            mode=charging_mode,
            kwh=kwh,
            status=RequestStatus.WAITING,
            created_at=datetime.now(),
        )
        request = req_repo.save(request)

        seq = req_repo.get_next_seq(charging_mode)
        prefix = "F" if charging_mode == ChargingMode.FAST else "T"
        code = f"{prefix}{seq}"

        qn = QueueNumber(
            code=code,
            mode=charging_mode,
            seq=seq,
            request_id=request.id,
            created_at=datetime.now(),
        )
        req_repo.save_queue_number(qn)

        entry = PileQueueEntry(
            request_id=request.id,
            user_id=user_id,
            kwh=kwh,
            mode=charging_mode,
            queue_code=code,
            queue_seq=seq,
        )
        scheduler.waiting_queue.enqueue(entry)
        scheduler.try_dispatch(db)

        return {
            "request_id": request.id,
            "queue_code": code,
            "mode": mode,
            "kwh": kwh,
            "status": request.status.value,
        }

    def modify_charging_mode(self, user_id: int, new_mode: str, db: Session) -> dict:
        req_repo = RequestRepo(db)
        active = req_repo.find_active_by_user(user_id)
        if not active:
            raise ValueError("无活跃充电请求")
        if active.status != RequestStatus.WAITING:
            raise ValueError("仅在等候区可修改充电模式；进入充电区后请先取消再重新排队")

        new_charging_mode = ChargingMode(new_mode)
        scheduler.waiting_queue.remove_by_request_id(active.id)

        old_qn = req_repo.find_queue_number_by_request(active.id)
        if old_qn:
            req_repo.delete_queue_number(old_qn)

        active.mode = new_charging_mode
        req_repo.update(active)

        seq = req_repo.get_next_seq(new_charging_mode)
        prefix = "F" if new_charging_mode == ChargingMode.FAST else "T"
        code = f"{prefix}{seq}"
        new_qn = QueueNumber(
            code=code, mode=new_charging_mode, seq=seq,
            request_id=active.id, created_at=datetime.now()
        )
        req_repo.save_queue_number(new_qn)

        entry = PileQueueEntry(
            request_id=active.id, user_id=user_id,
            kwh=active.kwh, mode=new_charging_mode, queue_code=code, queue_seq=seq,
        )
        scheduler.waiting_queue.enqueue(entry)
        scheduler.try_dispatch(db)

        return {"request_id": active.id, "new_mode": new_mode, "queue_code": code, "kwh": active.kwh}

    def modify_charging_amount(self, user_id: int, new_kwh: float, db: Session) -> dict:
        req_repo = RequestRepo(db)
        active = req_repo.find_active_by_user(user_id)
        if not active:
            raise ValueError("无活跃充电请求")
        if active.status != RequestStatus.WAITING:
            raise ValueError("仅在等候区可修改充电量；进入充电区后请先取消再重新排队")

        active.kwh = new_kwh
        req_repo.update(active)

        for lst in [scheduler.waiting_queue.fast_list, scheduler.waiting_queue.trickle_list]:
            for entry in lst:
                if entry.request_id == active.id:
                    entry.kwh = new_kwh
                    break

        qn = req_repo.find_queue_number_by_request(active.id)
        return {"request_id": active.id, "new_kwh": new_kwh, "queue_code": qn.code if qn else None}

    def cancel_charging(self, user_id: int, db: Session) -> dict:
        req_repo = RequestRepo(db)
        pile_repo = PileRepo(db)
        active = req_repo.find_active_by_user(user_id)
        if not active:
            raise ValueError("无活跃充电请求")

        bill = None

        if active.status == RequestStatus.WAITING:
            scheduler.waiting_queue.remove_by_request_id(active.id)
        elif active.status == RequestStatus.QUEUED:
            result = scheduler.remove_from_pile_queue(active.id)
            if result:
                scheduler.try_dispatch(db)
        elif active.status == RequestStatus.CHARGING:
            pos_info = scheduler.get_pile_queue_position(active.id)
            if pos_info:
                pile_id, pos = pos_info
                if pos != 0:
                    scheduler.remove_from_pile_queue(active.id)
                    scheduler.try_dispatch(db)
                else:
                    session = db.query(ChargingSession).filter(
                        ChargingSession.request_id == active.id,
                        ChargingSession.status == SessionStatus.RUNNING
                    ).first()
                    pile = pile_repo.find_by_id(pile_id)
                    if session and pile:
                        bill = session_service.finalize_session(
                            session, pile, db, request_status=RequestStatus.CANCELLED
                        )
                    scheduler.on_charging_complete(pile_id, db)

        active.status = RequestStatus.CANCELLED
        active.cancelled_at = datetime.now()
        req_repo.update(active)

        qn = req_repo.find_queue_number_by_request(active.id)
        if qn:
            req_repo.delete_queue_number(qn)

        scheduler.try_dispatch(db)

        return {
            "request_id": active.id,
            "status": "CANCELLED",
            "bill_id": bill.id if bill else None,
        }

    def view_queue_number(self, user_id: int, db: Session) -> Optional[dict]:
        req_repo = RequestRepo(db)
        active = req_repo.find_active_by_user(user_id)
        if not active:
            return None
        qn = req_repo.find_queue_number_by_request(active.id)
        if not qn:
            return None
        return {
            "request_id": active.id,
            "code": qn.code,
            "mode": qn.mode.value,
            "seq": qn.seq,
            "kwh": active.kwh,
            "status": active.status.value,
        }

    def view_waiting_count(self, user_id: int, db: Session) -> dict:
        req_repo = RequestRepo(db)
        active = req_repo.find_active_by_user(user_id)
        if not active:
            raise ValueError("无活跃充电请求")

        mode = active.mode
        if active.status == RequestStatus.WAITING:
            count = scheduler.waiting_queue.count_ahead_of(active.id, mode)
            if count < 0:
                count = 0
        elif active.status in (RequestStatus.QUEUED, RequestStatus.CHARGING):
            pos_info = scheduler.get_pile_queue_position(active.id)
            count = pos_info[1] if pos_info else 0
        else:
            count = 0

        return {"waiting_count": count, "mode": mode.value}
