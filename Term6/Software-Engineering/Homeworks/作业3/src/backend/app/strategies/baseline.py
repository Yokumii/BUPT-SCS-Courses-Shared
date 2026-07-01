from typing import Optional

from app.strategies.base import DispatchPolicy, DispatchCandidate, PileSlot


class BaselinePolicy(DispatchPolicy):

    def select_pile(
        self, candidate: DispatchCandidate, available_piles: list[PileSlot]
    ) -> Optional[int]:
        matching = [p for p in available_piles if p.pile_type == candidate.mode]
        if not matching:
            return None

        charge_time_fn = lambda p: candidate.kwh / p.power
        best = min(matching, key=lambda p: p.current_wait_hours + charge_time_fn(p))
        return best.pile_id

    def select_batch(
        self, candidates: list[DispatchCandidate], available_piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        result = []
        remaining_piles = list(available_piles)
        for c in candidates:
            pile_id = self.select_pile(c, remaining_piles)
            if pile_id is not None:
                result.append((c.request_id, pile_id))
                remaining_piles = [p for p in remaining_piles if p.pile_id != pile_id]
        return result
