#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import os
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from divide_tt import TennisTournament


class TestTennisTournament:
    
    @pytest.fixture
    def tournament(self):
        return TennisTournament()
    
    def validate_schedule(self, schedule, num_players):
        """验证赛程表的正确性"""
        if num_players == 1:
            return schedule[1][1] == 1
        
        # 检查每个选手是否与其他所有选手各赛一次
        for i in range(1, num_players + 1):
            opponents = set()
            max_col = num_players + 1 if num_players % 2 == 1 else num_players
            
            for j in range(2, max_col + 1):
                if schedule[i][j] > 0 and schedule[i][j] <= num_players:
                    opponents.add(schedule[i][j])
            
            if len(opponents) != num_players - 1:
                return False
        
        return True
    
    def run_test(self, tournament, test_name, num_players):
        print(f"\n{test_name} (n={num_players}):")
        print("-" * 40)
        
        start_time = time.time()
        schedule = tournament.solve(num_players)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000000
        
        is_valid = self.validate_schedule(schedule, num_players)
        
        status = "✓ 通过" if is_valid else "✗ 失败"
        print(f"正确性: {status}")
        print(f"执行时间: {execution_time:.0f} 微秒")
        
        # 仅打印小规模测试的赛程表（阈值40）
        if num_players <= 40:
            print("比赛日程表:")
            tournament.print_schedule(num_players)
        
        return is_valid
    
    # 基本功能测试
    def test_basic_even_players(self, tournament):
        """输入 12：测试偶数人数"""
        assert self.run_test(tournament, "输入 12：测试偶数人数", 12)
    
    def test_basic_odd_players(self, tournament):
        """输入 7：测试奇数人数"""
        assert self.run_test(tournament, "输入 7：测试奇数人数", 7)
    
    # 边界情况测试
    def test_boundary_single_player(self, tournament):
        """输入 1：测试单人情况"""
        assert self.run_test(tournament, "输入 1：测试单人情况", 1)
    
    def test_boundary_two_players(self, tournament):
        """输入 2：测试最小偶数情况"""
        assert self.run_test(tournament, "输入 2：测试最小偶数情况", 2)
    
    def test_boundary_three_players(self, tournament):
        """输入 3：测试最小奇数情况"""
        assert self.run_test(tournament, "输入 3：测试最小奇数情况", 3)
    
    # 输出效果测试
    def test_boundary_print_threshold(self, tournament):
        """输入 40：输出效果测试（打印阈值：40）"""
        assert self.run_test(tournament, "输入 40：输出效果测试", 40)
    
    # 大规模测试
    def test_medium_scale_performance(self, tournament):
        """输入 2000：测试较大规模"""
        assert self.run_test(tournament, "输入 2000：测试较大规模", 2000)
    
    def test_large_scale_performance(self, tournament):
        """输入 10000：测试大规模"""
        assert self.run_test(tournament, "输入 10000：测试大规模", 10000)
    
    # 特例测试
    def test_power_of_two_players(self, tournament):
        """输入 32：测试2的幂次"""
        assert self.run_test(tournament, "输入 32：测试2的幂次", 32)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s", "--tb=short"])