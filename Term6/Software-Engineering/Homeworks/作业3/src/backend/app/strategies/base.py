from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class DispatchCandidate:
    request_id: int
    user_id: int
    mode: str
    kwh: float
    queue_seq: int


@dataclass
class PileSlot:
    pile_id: int
    pile_type: str
    power: float
    current_wait_hours: float


class DispatchPolicy(ABC):

    @abstractmethod
    def select_pile(
        self, candidate: DispatchCandidate, available_piles: list[PileSlot]
    ) -> Optional[int]:
        pass

    @abstractmethod
    def select_batch(
        self, candidates: list[DispatchCandidate], available_piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        pass
