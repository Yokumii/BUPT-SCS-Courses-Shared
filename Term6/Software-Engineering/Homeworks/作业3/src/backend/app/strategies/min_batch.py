from typing import Optional

from app.strategies.base import DispatchPolicy, DispatchCandidate, PileSlot


class MinBatchPolicy(DispatchPolicy):

    def select_pile(
        self, candidate: DispatchCandidate, available_piles: list[PileSlot]
    ) -> Optional[int]:
        if not available_piles:
            return None
        best = min(available_piles, key=lambda p: p.current_wait_hours + candidate.kwh / p.power)
        return best.pile_id

    def select_batch(
        self, candidates: list[DispatchCandidate], available_piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        if not candidates or not available_piles:
            return []
        return self._greedy_assign(candidates, available_piles)

    def _greedy_assign(
        self, candidates: list[DispatchCandidate], piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        sorted_cands = sorted(candidates, key=lambda c: c.kwh, reverse=True)
        pile_loads = {p.pile_id: p.current_wait_hours for p in piles}
        pile_map = {p.pile_id: p for p in piles}
        assignment = []

        for c in sorted_cands:
            best_pile_id = min(pile_loads, key=lambda pid: pile_loads[pid] + c.kwh / pile_map[pid].power)
            assignment.append((c.request_id, best_pile_id))
            pile_loads[best_pile_id] += c.kwh / pile_map[best_pile_id].power

        return assignment
