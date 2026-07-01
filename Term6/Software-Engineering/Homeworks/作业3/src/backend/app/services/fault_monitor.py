from datetime import datetime

from sqlalchemy.orm import Session

from app.models.pile import PileStatus
from app.models.charging import SessionStatus, RequestStatus
from app.repositories.pile_repo import PileRepo
from app.services.scheduler import scheduler
from app.services.session_service import session_service


class FaultMonitor:

    def handle_fault(self, pile_id: int, db: Session, strategy: str = "PRIORITY") -> dict:
        pile_repo = PileRepo(db)
        pile = pile_repo.find_by_id(pile_id)
        if not pile:
            return {"error": "Pile not found"}
        if strategy not in ("PRIORITY", "TIME_ORDER"):
            return {"error": "Invalid fault scheduling strategy"}

        pile.status = PileStatus.FAULT
        pile_repo.update(pile)
        pq = scheduler.pile_queues.get(pile_id)
        if pq:
            pq.status = PileStatus.FAULT

        active_session = pile_repo.find_active_session(pile_id)
        bill = None
        if active_session:
            bill = session_service.finalize_session(
                active_session, pile, db, request_status=RequestStatus.ENDED
            )
            pq = scheduler.pile_queues.get(pile_id)
            if pq and pq.entries:
                pq.entries.pop(0)

        dispatched = scheduler.on_pile_fault(pile_id, db, strategy=strategy)

        return {
            "pile_id": pile_id,
            "strategy": strategy,
            "bill": {"id": bill.id, "total_fee": bill.total_fee} if bill else None,
            "rescheduled": len(dispatched),
        }

    def handle_recovery(self, pile_id: int, db: Session) -> dict:
        pile_repo = PileRepo(db)
        pile = pile_repo.find_by_id(pile_id)
        if not pile:
            return {"error": "Pile not found"}

        pile.status = PileStatus.ONLINE
        pile.last_started_at = datetime.now()
        pile_repo.update(pile)
        pq = scheduler.pile_queues.get(pile_id)
        if pq:
            pq.status = PileStatus.ONLINE

        dispatched = scheduler.on_pile_recovered(pile_id, db)

        return {
            "pile_id": pile_id,
            "rescheduled": len(dispatched),
        }


fault_monitor = FaultMonitor()
