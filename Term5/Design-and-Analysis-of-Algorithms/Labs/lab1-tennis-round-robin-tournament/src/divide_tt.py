#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from typing import List, Optional


class TennisTournament:
    
    def __init__(self):
        self.schedule: List[List[int]] = []
        self.bye_players: List[int] = []
        self.num_players = 0
    
    def print_schedule(self, num: int) -> None:
        """
        打印比赛日程表
        """
        if num % 2 == 0:
            for i in range(1, num + 1):
                row = f"{self.schedule[i][1]:4d}:"
                for j in range(2, num + 1):
                    row += f"{self.schedule[i][j]:4d}"
                print(row)
        else:
            for i in range(1, num + 1):
                row = f"{self.schedule[i][1]:4d}:"
                for j in range(2, num + 2):
                    if self.schedule[i][j] == num + 1:
                        row += f"{'/' :>4s}"  # 右对齐轮空符号
                    else:
                        row += f"{self.schedule[i][j]:4d}"
                print(row)
        print()
    
    def handle_even(self, num: int) -> None:
        # half 为偶数，交叉复制
        half = num // 2
        for i in range(1, half + 1):
            for j in range(1, half + 1):
                # 右上角：左上角 + half
                self.schedule[i][j + half] = self.schedule[i][j] + half
                # 左下角：复制右上角
                self.schedule[i + half][j] = self.schedule[i][j + half]
                # 右下角：复制左上角
                self.schedule[i + half][j + half] = self.schedule[i][j]
    
    def handle_odd(self, num: int) -> None:
        # half 为奇数，轮空修补+跨组循环配对
        half = num // 2
        
        for i in range(1, half + 1):
            self.bye_players[i] = half + i
            self.bye_players[half + i] = self.bye_players[i]
        
        # 处理左半
        for i in range(1, half + 1):
            for j in range(1, half + 2):
                if self.schedule[i][j] > half:  # 当前选手轮空
                    # 将轮空改为跨组对手
                    self.schedule[i][j] = self.bye_players[i]
                    # 对称位置记录配对
                    self.schedule[half + i][j] = (self.bye_players[i] + half) % num
                else:  # 非轮空情况
                    # 跨组平移
                    self.schedule[half + i][j] = self.schedule[i][j] + half
        
        # 处理右半
        for i in range(1, half + 1):
            for j in range(2, half + 1):
                # 计算对手：B((i+j-2) mod half + 1)
                opponent_idx = (i + j - 2) % half + 1
                opponent = self.bye_players[opponent_idx]
                self.schedule[i][half + j] = opponent
                self.schedule[opponent][half + j] = i
    
    def copy_schedule(self, num: int) -> None:
        half = num // 2
        if half > 1 and half % 2 == 1:
            self.handle_odd(num)
        else:
            self.handle_even(num)
    
    def generate_schedule(self, num: int) -> None:
        """
        递归生成赛程
        """
        if num == 1:
            self.schedule[1][1] = 1
            return
        
        if num % 2 == 1:
            self.generate_schedule(num + 1)
            return
        
        self.generate_schedule(num // 2)
        self.copy_schedule(num)
    
    def solve(self, num_players: int) -> List[List[int]]:
        self.num_players = num_players
        
        # 创建数组
        max_size = num_players + 1 if num_players % 2 == 1 else num_players
        max_cols = max_size + 1 if max_size % 2 == 1 else max_size
        
        self.schedule = [[0 for _ in range(max_cols + 1)] for _ in range(max_size + 1)]
        self.bye_players = [0 for _ in range(max_size + 1)]
        
        # 生成赛程
        self.generate_schedule(num_players)
        
        return self.schedule
    
    def run(self) -> None:
        try:
            num_players = int(input("请输入选手数量: "))
            
            if num_players <= 0:
                print("选手数量必须大于0")
                return
            
            # 开始计时
            start_time = time.time()
            
            # 生成赛程
            self.solve(num_players)
            
            # 停止计时
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000000  # 转换为微秒
            
            # 输出结果
            if num_players <= 40:
                print("生成的赛程安排:")
                self.print_schedule(num_players)
            
            print(f"执行时间: {execution_time:.0f} 微秒")
            
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"发生错误: {e}")

def main():   
    tournament = TennisTournament()
    tournament.run()

if __name__ == "__main__":
    main()
