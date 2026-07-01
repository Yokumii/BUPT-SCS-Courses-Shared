from typing import Optional
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.config import settings
from app.models.charging import ChargingRequest, ChargingSession, QueueNumber, RequestStatus, SessionStatus, ChargingMode
from app.models.pile import PileStatus
from app.models.billing import SchedulingMode
from app.strategies.base import DispatchPolicy, DispatchCandidate, PileSlot
from app.strategies.baseline import BaselinePolicy
from app.strategies.min_single import MinSinglePolicy
from app.strategies.min_batch import MinBatchPolicy
from app.repositories.pile_repo import PileRepo
from app.repositories.request_repo import RequestRepo
from app.services.time_service import time_service


@dataclass
class PileQueueEntry:
    request_id: int
    user_id: int
    kwh: float
    mode: str
    queue_code: str
    queue_seq: int = 0


@dataclass
class PileQueueState:
    pile_id: int
    pile_type: str
    power: float
    capacity: int
    status: PileStatus
    entries: list[PileQueueEntry] = field(default_factory=list)

    @property
    def is_full(self) -> bool:
        return len(self.entries) >= self.capacity

    @property
    def has_vacancy(self) -> bool:
        return len(self.entries) < self.capacity

    @property
    def current_wait_hours(self) -> float:
        return sum(entry.kwh / self.power for entry in self.entries)


class WaitingQueue:

    def __init__(self):
        self.fast_list: list[PileQueueEntry] = []
        self.trickle_list: list[PileQueueEntry] = []
        self._paused = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    def pause_call(self):
        self._paused = True

    def resume_call(self):
        self._paused = False

    def _list_for_mode(self, mode: str) -> list[PileQueueEntry]:
        return self.fast_list if mode == ChargingMode.FAST else self.trickle_list

    def enqueue(self, entry: PileQueueEntry):
        self._list_for_mode(entry.mode).append(entry)

    def enqueue_front_ordered(self, entries: list[PileQueueEntry]):
        for mode in [ChargingMode.FAST, ChargingMode.TRICKLE]:
            mode_entries = sorted([e for e in entries if e.mode == mode], key=lambda e: e.queue_seq)
            if mode_entries:
                lst = self._list_for_mode(mode)
                lst[:0] = mode_entries

    def dequeue_by_mode(self, mode: str) -> Optional[PileQueueEntry]:
        lst = self._list_for_mode(mode)
        if lst:
            return lst.pop(0)
        return None

    def peek_by_mode(self, mode: str) -> Optional[PileQueueEntry]:
        lst = self._list_for_mode(mode)
        return lst[0] if lst else None

    def size(self, mode: Optional[str] = None) -> int:
        if mode == ChargingMode.FAST:
            return len(self.fast_list)
        elif mode == ChargingMode.TRICKLE:
            return len(self.trickle_list)
        return len(self.fast_list) + len(self.trickle_list)

    def total_capacity(self) -> int:
        return settings.WAITING_AREA_SIZE

    def is_full(self) -> bool:
        return self.size() >= settings.WAITING_AREA_SIZE

    def remove_by_request_id(self, request_id: int) -> Optional[PileQueueEntry]:
        for lst in [self.fast_list, self.trickle_list]:
            for i, entry in enumerate(lst):
                if entry.request_id == request_id:
                    return lst.pop(i)
        return None

    def count_ahead_of(self, request_id: int, mode: str) -> int:
        lst = self._list_for_mode(mode)
        for i, entry in enumerate(lst):
            if entry.request_id == request_id:
                return i
        return -1

    def drain_all(self) -> list[PileQueueEntry]:
        all_entries = self.fast_list + self.trickle_list
        self.fast_list = []
        self.trickle_list = []
        return all_entries

    def peek_top_by_mode(self, mode: str, count: int) -> list[PileQueueEntry]:
        return self._list_for_mode(mode)[:count]


class Scheduler:

    def __init__(self):
        self.policy: DispatchPolicy = BaselinePolicy()
        self.waiting_queue = WaitingQueue()
        self.pile_queues: dict[int, PileQueueState] = {}
        self._initialized = False

    def initialize(self, db: Session):
        if self._initialized:
            return
        pile_repo = PileRepo(db)
        piles = pile_repo.find_all()
        for pile in piles:
            self.pile_queues[pile.id] = PileQueueState(
                pile_id=pile.id,
                pile_type=pile.pile_type,
                power=pile.power,
                capacity=settings.CHARGING_QUEUE_LEN,
                status=pile.status,
            )
        req_repo = RequestRepo(db)
        for mode in [ChargingMode.FAST, ChargingMode.TRICKLE]:
            reqs = req_repo.list_by_mode(mode)
            for req in reqs:
                qn = req_repo.find_queue_number_by_request(req.id)
                if not qn:
                    continue
                entry = PileQueueEntry(
                    request_id=req.id,
                    user_id=req.user_id,
                    kwh=req.kwh,
                    mode=req.mode,
                    queue_code=qn.code,
                    queue_seq=qn.seq,
                )
                if req.status == RequestStatus.WAITING:
                    self.waiting_queue.enqueue(entry)
                elif req.status == RequestStatus.QUEUED:
                    session = db.query(ChargingSession).filter(
                        ChargingSession.request_id == req.id,
                        ChargingSession.status == SessionStatus.RUNNING
                    ).first()
                    if session and session.pile_id in self.pile_queues:
                        self.pile_queues[session.pile_id].entries.append(entry)

        self._initialized = True

    def set_policy(self, mode: SchedulingMode):
        if mode == SchedulingMode.BASELINE:
            self.policy = BaselinePolicy()
        elif mode == SchedulingMode.MIN_SINGLE:
            self.policy = MinSinglePolicy()
        elif mode == SchedulingMode.MIN_BATCH:
            self.policy = MinBatchPolicy()

    def get_available_piles(self, mode: Optional[str] = None) -> list[PileSlot]:
        result = []
        for pq in self.pile_queues.values():
            if pq.status != PileStatus.ONLINE or not pq.has_vacancy:
                continue
            if mode and pq.pile_type != mode:
                continue
            result.append(PileSlot(
                pile_id=pq.pile_id,
                pile_type=pq.pile_type,
                power=pq.power,
                current_wait_hours=pq.current_wait_hours,
            ))
        return result

    def try_dispatch(self, db: Session) -> list[tuple[int, int]]:
        if self.waiting_queue.is_paused:
            return []

        if isinstance(self.policy, MinBatchPolicy):
            return self._try_batch_dispatch(db)
        if isinstance(self.policy, MinSinglePolicy):
            return self._try_single_dispatch(db)
        return self._try_baseline_dispatch(db)

    def _candidate_from_entry(self, entry: PileQueueEntry) -> DispatchCandidate:
        return DispatchCandidate(
            request_id=entry.request_id,
            user_id=entry.user_id,
            mode=entry.mode,
            kwh=entry.kwh,
            queue_seq=entry.queue_seq,
        )

    def _try_baseline_dispatch(self, db: Session) -> list[tuple[int, int]]:
        dispatched = []
        for mode in [ChargingMode.FAST, ChargingMode.TRICKLE]:
            while True:
                available = self.get_available_piles(mode)
                entry = self.waiting_queue.peek_by_mode(mode)
                if not available or not entry:
                    break
                pile_id = self.policy.select_pile(self._candidate_from_entry(entry), available)
                if pile_id is None:
                    break
                self.waiting_queue.dequeue_by_mode(mode)
                self._assign_to_pile(entry, pile_id, db)
                dispatched.append((entry.request_id, pile_id))
        return dispatched

    def _try_single_dispatch(self, db: Session) -> list[tuple[int, int]]:
        available = self.get_available_piles()
        if len(available) < 2:
            return self._try_baseline_dispatch(db)

        candidates = []
        for mode in [ChargingMode.FAST, ChargingMode.TRICKLE]:
            mode_available = [p for p in available if p.pile_type == mode]
            for e in self.waiting_queue.peek_top_by_mode(mode, len(mode_available)):
                candidates.append(self._candidate_from_entry(e))

        assignments = self.policy.select_batch(candidates, available) if candidates else []
        dispatched = []
        for req_id, pile_id in assignments:
            entry = self.waiting_queue.remove_by_request_id(req_id)
            if entry:
                self._assign_to_pile(entry, pile_id, db)
                dispatched.append((req_id, pile_id))
        return dispatched

    def _try_batch_dispatch(self, db: Session) -> list[tuple[int, int]]:
        total_pile_capacity = sum(pq.capacity for pq in self.pile_queues.values())
        charging_area_count = sum(len(pq.entries) for pq in self.pile_queues.values())
        total_vehicles = self.waiting_queue.size() + charging_area_count
        total_capacity = total_pile_capacity + settings.WAITING_AREA_SIZE

        if total_vehicles < total_capacity:
            return []

        all_entries = self.waiting_queue.drain_all()
        candidates = [self._candidate_from_entry(e) for e in all_entries]
        all_piles = [
            PileSlot(pile_id=pq.pile_id, pile_type=pq.pile_type,
                     power=pq.power, current_wait_hours=pq.current_wait_hours)
            for pq in self.pile_queues.values()
            if pq.status == PileStatus.ONLINE and pq.has_vacancy
        ]

        assignments = self.policy.select_batch(candidates, all_piles)
        dispatched = []
        assigned_ids = set()
        for req_id, pile_id in assignments:
            entry = next((e for e in all_entries if e.request_id == req_id), None)
            if entry:
                self._assign_to_pile(entry, pile_id, db)
                dispatched.append((req_id, pile_id))
                assigned_ids.add(req_id)

        for e in all_entries:
            if e.request_id not in assigned_ids:
                self.waiting_queue.enqueue(e)
        return dispatched

    def _assign_to_pile(self, entry: PileQueueEntry, pile_id: int, db: Session):
        pq = self.pile_queues.get(pile_id)
        if not pq or pq.is_full:
            return
        if any(e.request_id == entry.request_id for e in pq.entries):
            return
        pq.entries.append(entry)

        req_repo = RequestRepo(db)
        req = req_repo.find_by_id(entry.request_id)
        if req:
            req.status = RequestStatus.QUEUED
            req_repo.update(req)

        if len(pq.entries) == 1:
            self._start_charging(entry, pile_id, db)

    def _start_charging(self, entry: PileQueueEntry, pile_id: int, db: Session):
        req_repo = RequestRepo(db)
        pile_repo = PileRepo(db)

        req = req_repo.find_by_id(entry.request_id)
        if not req:
            return
        existing = db.query(ChargingSession).filter(
            ChargingSession.request_id == entry.request_id,
            ChargingSession.status == SessionStatus.RUNNING,
        ).first()
        if existing:
            return

        req.status = RequestStatus.CHARGING
        req_repo.update(req)

        session = ChargingSession(
            pile_id=pile_id,
            request_id=entry.request_id,
            user_id=entry.user_id,
            status=SessionStatus.RUNNING,
            start_time=time_service.now(),
        )
        pile_repo.save_session(session)

    def on_charging_complete(self, pile_id: int, db: Session):
        pq = self.pile_queues.get(pile_id)
        if not pq or not pq.entries:
            return
        pq.entries.pop(0)
        if pq.entries:
            self._start_charging(pq.entries[0], pile_id, db)

    def on_pile_fault(self, pile_id: int, db: Session, strategy: str = "PRIORITY") -> list[tuple[int, int]]:
        pq = self.pile_queues.get(pile_id)
        if not pq:
            return []

        self.waiting_queue.pause_call()
        try:
            displaced = list(pq.entries)
            pq.entries.clear()
            displaced.sort(key=lambda e: e.queue_seq)

            if strategy == "TIME_ORDER":
                same_type_non_charging = []
                for other_id, other_q in self.pile_queues.items():
                    if other_id == pile_id or other_q.pile_type != pq.pile_type:
                        continue
                    if len(other_q.entries) > 1:
                        same_type_non_charging.extend(other_q.entries[1:])
                        other_q.entries = other_q.entries[:1]
                displaced.extend(same_type_non_charging)
                displaced.sort(key=lambda e: e.queue_seq)

            return self._redispatch_entries(displaced, db, front_if_waiting=True)
        finally:
            self.waiting_queue.resume_call()
            self.try_dispatch(db)

    def on_pile_recovered(self, pile_id: int, db: Session) -> list[tuple[int, int]]:
        pq = self.pile_queues.get(pile_id)
        if not pq:
            return []

        same_type_non_charging = []
        for other_id, other_q in self.pile_queues.items():
            if other_id == pile_id or other_q.pile_type != pq.pile_type:
                continue
            if len(other_q.entries) > 1:
                same_type_non_charging.extend(other_q.entries[1:])
                other_q.entries = other_q.entries[:1]

        if not same_type_non_charging:
            return self.try_dispatch(db)

        self.waiting_queue.pause_call()
        try:
            same_type_non_charging.sort(key=lambda e: e.queue_seq)
            return self._redispatch_entries(same_type_non_charging, db, front_if_waiting=True)
        finally:
            self.waiting_queue.resume_call()
            self.try_dispatch(db)

    def _redispatch_entries(self, entries: list[PileQueueEntry], db: Session, front_if_waiting: bool) -> list[tuple[int, int]]:
        req_repo = RequestRepo(db)
        dispatched = []
        waiting = []
        for entry in entries:
            available = self.get_available_piles(entry.mode)
            target = self.policy.select_pile(self._candidate_from_entry(entry), available) if available else None
            if target:
                self._assign_to_pile(entry, target, db)
                dispatched.append((entry.request_id, target))
            else:
                req = req_repo.find_by_id(entry.request_id)
                if req:
                    req.status = RequestStatus.WAITING
                    req_repo.update(req)
                waiting.append(entry)
        if waiting:
            if front_if_waiting:
                self.waiting_queue.enqueue_front_ordered(waiting)
            else:
                for entry in waiting:
                    self.waiting_queue.enqueue(entry)
        return dispatched

    def remove_from_pile_queue(self, request_id: int) -> Optional[tuple[int, int]]:
        for pid, pq in self.pile_queues.items():
            for i, entry in enumerate(pq.entries):
                if entry.request_id == request_id:
                    pq.entries.pop(i)
                    return (pid, i)
        return None

    def get_pile_queue_position(self, request_id: int) -> Optional[tuple[int, int]]:
        for pid, pq in self.pile_queues.items():
            for i, entry in enumerate(pq.entries):
                if entry.request_id == request_id:
                    return (pid, i)
        return None


scheduler = Scheduler()
