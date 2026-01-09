#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import pytest

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from knapsack import knapsack  # noqa: E402


def validate_solution(weights, values, capacity, result):
    if isinstance(result, tuple):
        max_value, items = result
    else:
        # 函数在空输入/容量为0时可能直接返回数值
        max_value, items = result, []

    # 索引合法且唯一
    seen = set()
    total_weight = 0
    for idx in items:
        assert 0 <= idx < len(weights), f"非法索引 {idx}"
        assert idx not in seen, f"重复索引 {idx}"
        seen.add(idx)
        total_weight += weights[idx]

    assert total_weight <= capacity, f"总重量 {total_weight} 超出容量 {capacity}"
    # 验证价值
    calc_value = sum(values[i] for i in items)
    assert calc_value == max_value, f"价值不一致：计算 {calc_value} vs 返回 {max_value}"
    return max_value, items


class TestKnapsackDP:
    def run_case(self, name, weights, values, capacity, expected_value=None):
        start = time.time()
        result = knapsack(weights, values, capacity)
        duration_us = (time.time() - start) * 1_000_000

        max_value, items = validate_solution(weights, values, capacity, result)
        if expected_value is not None:
            assert max_value == expected_value, f"{name}: 期望 {expected_value} 实际 {max_value}"

        print(f"\n{name}")
        print("-" * 60)
        print(f"weights={weights}")
        print(f"values ={values}")
        print(f"capacity={capacity}")
        print(f"max_value={max_value}, items={items}")
        print(f"执行时间: {duration_us:.0f} 微秒")
        return max_value, items

    # 基础功能
    def test_sample_case(self):
        weights = [10, 40, 55, 20]
        values = [20, 120, 55, 100]
        capacity = 100
        # 最优：物品 0,1,3 => 20 + 120 + 100 = 240
        self.run_case("示例用例", weights, values, capacity, expected_value=240)

    def test_exact_fill(self):
        weights = [2, 3, 4]
        values = [4, 5, 6]
        capacity = 5
        # 选 0,1 => 9
        self.run_case("恰好填满", weights, values, capacity, expected_value=9)

    def test_all_fit(self):
        weights = [1, 2, 3]
        values = [6, 10, 12]
        capacity = 10
        # 全部装入 => 28
        self.run_case("容量充足", weights, values, capacity, expected_value=28)

    # 边界情况
    def test_empty_items(self):
        self.run_case("空物品列表", [], [], 50, expected_value=0)

    def test_zero_capacity(self):
        weights = [5, 6, 7]
        values = [10, 20, 30]
        self.run_case("容量为0", weights, values, 0, expected_value=0)

    def test_single_item_fit(self):
        weights = [5]
        values = [10]
        self.run_case("单个物品可装", weights, values, 5, expected_value=10)

    def test_single_item_not_fit(self):
        weights = [5]
        values = [10]
        self.run_case("单个物品不可装", weights, values, 3, expected_value=0)

    # 特殊场景
    def test_choose_high_value(self):
        weights = [5, 4, 6]
        values = [10, 40, 30]
        capacity = 6
        # 应选物品1 (4,40)，剩余 2 容量无法放其他 => 40
        self.run_case("高价值优先", weights, values, capacity, expected_value=40)

    def test_duplicate_weights(self):
        weights = [4, 4, 4]
        values = [10, 20, 30]
        capacity = 8
        # 选 1 和 2 => 50
        self.run_case("相同重量不同价值", weights, values, capacity, expected_value=50)

    # 中等规模
    def test_medium_scale(self):
        n = 100
        weights = list(range(1, n + 1))
        values = [w * 2 for w in weights]
        capacity = 200
        # 单位价值一致，期望装最轻的若干个凑容量
        result_value, _ = self.run_case(f"中等规模 n={n}", weights, values, capacity)
        assert result_value > 0
    
    # 大规模
    def test_large_scale(self):
        n = 1000
        weights = list(range(1, n + 1))
        values = [w * 2 for w in weights]
        capacity = 2000
        # 单位价值一致，期望装最轻的若干个凑容量
        result_value, _ = self.run_case(f"大规模 n={n}", weights, values, capacity)
        assert result_value > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])

