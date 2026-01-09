#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import time


class PolygonTournament:

    def __init__(self) -> None:
        self.schedule: List[List[int]] = []
        self.num_players: int = 0

    def _init_matrix(self, n: int) -> None:
        max_size = n + 1 if n % 2 == 1 else n
        max_cols = max_size + 1 if max_size % 2 == 1 else max_size
        self.schedule = [[0 for _ in range(max_cols + 1)] for _ in range(max_size + 1)]
        for i in range(1, n + 1):
            self.schedule[i][1] = i

    def solve(self, n: int) -> List[List[int]]:
        self.num_players = n
        self._init_matrix(n)

        odd = (n % 2 == 1)
        num = n + 1 if odd else n
        days = n if odd else n - 1

        players = list(range(1, num + 1))

        # 旋转多边形：固定第一个，其余环形右移
        for d in range(days):
            # 形成配对
            for j in range(num // 2):
                a = players[j]
                b = players[num - 1 - j]

                # 处理轮空（奇数 n）
                if odd and (a == num or b == num):
                    real = b if a == num else a
                    # 列索引：天 d 对应矩阵列 2+d
                    self.schedule[real][2 + d] = n + 1
                    continue

                # 记录双方对手
                self.schedule[a][2 + d] = b
                self.schedule[b][2 + d] = a

            # 旋转：保持 players[0] 固定，其余右移一位
            head = players[0]
            tail = players[-1]
            middle = players[1:-1]
            players = [head, tail] + middle  # 等价于右旋 1 位

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
                    if self.schedule[i][j] == n + 1:
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

    poly = PolygonTournament()
    start = time.time()
    poly.solve(n)
    end = time.time()
    duration_us = (end - start) * 1_000_000
    if n <= 40:
        print("生成的赛程安排:")
        poly.print_schedule(n)
    print(f"执行时间: {duration_us:.0f} 微秒")


if __name__ == "__main__":
    main()

