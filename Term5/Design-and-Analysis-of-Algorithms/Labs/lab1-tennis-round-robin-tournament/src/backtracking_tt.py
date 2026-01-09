#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Set, Tuple
import time


class BacktrackingTournament:
    def __init__(self) -> None:
        self.schedule: List[List[int]] = []
        self.n: int = 0
        self.num_days: int = 0
        self.bye_symbol: int = 0

    def _init_matrix(self, n: int) -> None:
        max_size = n + 1 if n % 2 == 1 else n
        max_cols = max_size + 1 if max_size % 2 == 1 else max_size
        self.schedule = [[0 for _ in range(max_cols + 1)] for _ in range(max_size + 1)]
        for i in range(1, n + 1):
            self.schedule[i][1] = i

    def solve(self, n: int) -> List[List[int]]:
        self.n = n
        self._init_matrix(n)
        self.num_days = n if n % 2 == 1 else n - 1
        self.bye_symbol = n + 1 if n % 2 == 1 else 0

        total_pairs = n * (n - 1) // 2
        used_pairs: Set[Tuple[int, int]] = set()

        def schedule_day(day: int) -> bool:
            if day == self.num_days:
                # 所有天数排完，仅当所有两两对都被安排才算成功
                return len(used_pairs) == total_pairs

            col = 2 + day
            assigned: Set[int] = set()
            bye_used = False

            # 递归为当天安排配对
            def assign_next() -> bool:
                nonlocal bye_used
                if len(assigned) == n or (self.bye_symbol and len(assigned) == n - 1 and bye_used):
                    return schedule_day(day + 1)

                # 选择当天尚未安排的最小编号选手
                p = None
                for x in range(1, n + 1):
                    if x not in assigned:
                        p = x
                        break
                assert p is not None

                # 尝试：奇数 n 时给 p 轮空
                if self.bye_symbol and not bye_used:
                    self.schedule[p][col] = self.bye_symbol
                    assigned.add(p)
                    saved_bye = True
                    bye_used = True
                    if assign_next():
                        return True
                    # 回溯撤销轮空
                    self.schedule[p][col] = 0
                    assigned.remove(p)
                    bye_used = False

                # 尝试：为 p 选择对手 q
                for q in range(1, n + 1):
                    if q == p or q in assigned:
                        continue
                    a, b = (p, q) if p < q else (q, p)
                    if (a, b) in used_pairs:
                        continue
                    # 安排配对 p-q
                    self.schedule[p][col] = q
                    self.schedule[q][col] = p
                    assigned.add(p)
                    assigned.add(q)
                    used_pairs.add((a, b))
                    if assign_next():
                        return True
                    # 回溯撤销配对
                    used_pairs.remove((a, b))
                    assigned.remove(q)
                    assigned.remove(p)
                    self.schedule[p][col] = 0
                    self.schedule[q][col] = 0

                return False

            return assign_next()

        if not schedule_day(0):
            raise RuntimeError("回溯法在给定 n 上未找到解")
        return self.schedule

    def print_schedule(self, n: int) -> None:
        if n % 2 == 0:
            for i in range(1, n + 1):
                row = f"{self.schedule[i][1]:4d}:"
                for j in range(2, n + 1):
                    row += f"{self.schedule[i][j]:4d}"
                print(row)
        else:
            for i in range(1, n + 1):
                row = f"{self.schedule[i][1]:4d}:"
                for j in range(2, n + 2):
                    if self.schedule[i][j] == self.bye_symbol:
                        row += f"{'/' :>4s}"
                    else:
                        row += f"{self.schedule[i][j]:4d}"
                print(row)
        print()


def main():
    import sys

    if len(sys.argv) >= 2:
        n = int(sys.argv[1])
    else:
        n = int(input("请输入选手数量: "))

    bt = BacktrackingTournament()
    start = time.time()
    bt.solve(n)
    end = time.time()
    duration_us = (end - start) * 1_000_000
    if n <= 40:
        print("生成的赛程安排:")
        bt.print_schedule(n)
    print(f"执行时间: {duration_us:.0f} 微秒")


if __name__ == "__main__":
    main()

