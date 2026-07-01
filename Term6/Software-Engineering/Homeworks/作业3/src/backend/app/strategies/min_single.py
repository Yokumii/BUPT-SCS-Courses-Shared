from itertools import permutations
from typing import Optional

from app.strategies.base import DispatchPolicy, DispatchCandidate, PileSlot


class MinSinglePolicy(DispatchPolicy):

    def select_pile(
        self, candidate: DispatchCandidate, available_piles: list[PileSlot]
    ) -> Optional[int]:
        matching = [p for p in available_piles if p.pile_type == candidate.mode]
        if not matching:
            return None
        best = min(matching, key=lambda p: p.current_wait_hours + candidate.kwh / p.power)
        return best.pile_id

    def select_batch(
        self, candidates: list[DispatchCandidate], available_piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        if not candidates or not available_piles:
            return []

        fast_candidates = [c for c in candidates if c.mode == "FAST"]
        trickle_candidates = [c for c in candidates if c.mode == "TRICKLE"]
        fast_piles = [p for p in available_piles if p.pile_type == "FAST"]
        trickle_piles = [p for p in available_piles if p.pile_type == "TRICKLE"]

        result = []
        result.extend(self._optimize_group(fast_candidates, fast_piles))
        result.extend(self._optimize_group(trickle_candidates, trickle_piles))
        return result

    def _optimize_group(
        self, candidates: list[DispatchCandidate], piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        if not candidates or not piles:
            return []

        n = min(len(candidates), len(piles))
        candidates = candidates[:n]

        if n <= 6:
            return self._brute_force(candidates, piles)
        return self._greedy(candidates, piles)

    def _brute_force(
        self, candidates: list[DispatchCandidate], piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        best_score = float("inf")
        best_assignment = []

        for perm in permutations(range(len(piles)), len(candidates)):
            score = 0.0
            for i, pi in enumerate(perm):
                p = piles[pi]
                c = candidates[i]
                score += p.current_wait_hours + c.kwh / p.power
            if score < best_score:
                best_score = score
                best_assignment = [(candidates[i].request_id, piles[pi].pile_id) for i, pi in enumerate(perm)]

        return best_assignment

    def _greedy(
        self, candidates: list[DispatchCandidate], piles: list[PileSlot]
    ) -> list[tuple[int, int]]:
        result = []
        used_piles = set()
        sorted_candidates = sorted(candidates, key=lambda c: c.kwh, reverse=True)

        for c in sorted_candidates:
            best_pile = None
            best_score = float("inf")
            for p in piles:
                if p.pile_id in used_piles:
                    continue
                score = p.current_wait_hours + c.kwh / p.power
                if score < best_score:
                    best_score = score
                    best_pile = p
            if best_pile:
                result.append((c.request_id, best_pile.pile_id))
                used_piles.add(best_pile.pile_id)

        return result
