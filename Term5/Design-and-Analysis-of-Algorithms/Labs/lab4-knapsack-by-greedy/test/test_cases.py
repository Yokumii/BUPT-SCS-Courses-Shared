#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import os
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from knapsack import initialize_items, knapsack, Item


class TestKnapsack:
    
    def validate_solution(self, items, capacity, total_value, solution, expected_value=None):
        total_weight = 0.0
        calculated_value = 0.0
        
        # 创建物品ID到物品对象的映射
        item_map = {item.id: item for item in items}
        
        # 验证每个物品的放入重量
        for item_id, weight_taken in solution.items():
            if item_id not in item_map:
                return False, f"物品ID {item_id} 不存在"
            
            item = item_map[item_id]
            
            # 检查放入重量是否超过物品总重量
            if weight_taken > item.weight:
                return False, f"物品 {item_id} 放入重量 {weight_taken} 超过总重量 {item.weight}"
            
            # 检查放入重量是否为负
            if weight_taken < 0:
                return False, f"物品 {item_id} 放入重量 {weight_taken} 为负数"
            
            total_weight += weight_taken
            calculated_value += (weight_taken / item.weight) * item.value
        
        # 检查总重量是否超过容量
        if total_weight > capacity + 1e-6:  # 允许浮点误差
            return False, f"总重量 {total_weight} 超过容量 {capacity}"
        
        # 检查计算的总价值是否与返回的一致
        if abs(calculated_value - total_value) > 1e-6:
            return False, f"计算的总价值 {calculated_value} 与返回的总价值 {total_value} 不一致"
        
        # 如果提供了期望值，检查是否达到期望
        if expected_value is not None:
            if abs(total_value - expected_value) > 1e-6:
                return False, f"总价值 {total_value} 与期望值 {expected_value} 不一致"
        
        return True, "验证通过"
    
    def run_test(self, test_name, weights, values, capacity, expected_value=None, print_details=True):
        """运行单个测试用例"""
        if print_details:
            print(f"\n{test_name}:")
            print("-" * 60)
            print(f"物品重量: {weights}")
            print(f"物品价值: {values}")
            print(f"背包容量: {capacity}")
        
        # 初始化物品
        items = initialize_items(weights, values)
        
        # 记录原始物品顺序（用于验证）
        original_items = [Item(item.id, item.weight, item.value) for item in items]
        
        # 执行算法
        start_time = time.time()
        total_value, solution = knapsack(items, capacity)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000000  # 转换为微秒
        
        # 验证解的正确性
        is_valid, message = self.validate_solution(original_items, capacity, total_value, solution, expected_value)
        
        status = "✓ 通过" if is_valid else "✗ 失败"
        if print_details:
            print(f"正确性: {status}")
            if not is_valid:
                print(f"错误信息: {message}")
            print(f"总价值: {total_value:.2f}")
            print(f"执行时间: {execution_time:.0f} 微秒")
            print("各物品放入重量:")
            for i in range(1, len(weights) + 1):
                weight_taken = solution.get(i, 0)
                if weight_taken > 0:
                    print(f"  物品 {i}: {weight_taken:.2f} (总重量: {weights[i-1]}, 价值: {values[i-1]})")
        
        return is_valid
    
    # 基本功能测试
    def test_basic_functionality(self):
        """基本功能测试：标准背包问题"""
        weights = [10, 40, 55, 20]
        values = [20, 120, 55, 100]
        capacity = 100
        # 期望值：物品2全部(40,120) + 物品4全部(20,100) + 物品1全部(10,20) + 物品3部分(30/55, 30)
        # 120 + 100 + 20 + 30 = 270
        expected_value = 120 + 100 + 20 + (30 / 55) * 55  # 270.0
        assert self.run_test("基本功能测试：标准背包问题", weights, values, capacity, expected_value)
    
    def test_all_items_fit(self):
        """所有物品都能装下"""
        weights = [10, 20, 30]
        values = [60, 100, 120]
        capacity = 100
        expected_value = 60 + 100 + 120  # 280
        assert self.run_test("所有物品都能装下", weights, values, capacity, expected_value)
    
    def test_partial_items_only(self):
        """只能装部分物品"""
        weights = [50, 60, 70]
        values = [100, 120, 140]
        capacity = 80
        # 只能装物品1全部(50,100) + 物品2部分(30/60, 60)
        expected_value = 100 + (30 / 60) * 120  # 160.0
        assert self.run_test("只能装部分物品", weights, values, capacity, expected_value)
    
    # 边界情况测试
    def test_single_item(self):
        """单个物品"""
        weights = [50]
        values = [100]
        capacity = 60
        expected_value = 100.0
        assert self.run_test("单个物品（能装下）", weights, values, capacity, expected_value)
    
    def test_single_item_partial(self):
        """单个物品部分装入"""
        weights = [100]
        values = [200]
        capacity = 50
        expected_value = 100.0  # 50/100 * 200
        assert self.run_test("单个物品（部分装入）", weights, values, capacity, expected_value)
    
    def test_zero_capacity(self):
        """容量为0"""
        weights = [10, 20, 30]
        values = [60, 100, 120]
        capacity = 0
        expected_value = 0.0
        assert self.run_test("容量为0", weights, values, capacity, expected_value)
    
    def test_empty_items(self):
        """空物品列表"""
        weights = []
        values = []
        capacity = 100
        expected_value = 0.0
        assert self.run_test("空物品列表", weights, values, capacity, expected_value)
    
    def test_large_capacity(self):
        """容量远大于所有物品总重量"""
        weights = [10, 20, 30]
        values = [60, 100, 120]
        capacity = 1000
        expected_value = 60 + 100 + 120  # 280
        assert self.run_test("容量远大于所有物品总重量", weights, values, capacity, expected_value)
    
    # 特殊情况测试
    def test_same_unit_value(self):
        """单位价值相同"""
        weights = [10, 20, 30]
        values = [20, 40, 60]  # 单位价值都是2
        capacity = 50
        # 应该按顺序装入：10+20+20(部分30)
        expected_value = 20 + 40 + (20 / 30) * 60  # 100.0
        assert self.run_test("单位价值相同", weights, values, capacity, expected_value)
    
    def test_same_weight(self):
        """重量相同，价值不同"""
        weights = [10, 10, 10]
        values = [30, 20, 40]  # 单位价值：3, 2, 4
        capacity = 25
        # 应该优先装单位价值高的：物品3全部(10,40) + 物品1全部(10,30) + 物品2部分(5/10, 10)
        expected_value = 40 + 30 + (5 / 10) * 20  # 80.0
        assert self.run_test("重量相同，价值不同", weights, values, capacity, expected_value)
    
    def test_fractional_optimal(self):
        """分数背包的最优解验证"""
        weights = [10, 20]
        values = [60, 100]  # 单位价值：6, 5
        capacity = 15
        # 应该装物品1全部(10,60) + 物品2部分(5/20, 25)
        expected_value = 60 + (5 / 20) * 100  # 85.0
        assert self.run_test("分数背包最优解验证", weights, values, capacity, expected_value)
    
    # 大规模测试
    def test_medium_scale(self):
        """中等规模测试"""
        n = 100
        weights = [i for i in range(1, n + 1)]
        values = [i * 2 for i in range(1, n + 1)]  # 单位价值都是2
        capacity = 5000
        assert self.run_test(f"中等规模测试 (n={n})", weights, values, capacity, print_details=False)
    
    def test_large_scale(self):
        """大规模测试"""
        n = 1000
        weights = [i for i in range(1, n + 1)]
        values = [i * 3 for i in range(1, n + 1)]  # 单位价值都是3
        capacity = 50000
        assert self.run_test(f"大规模测试 (n={n})", weights, values, capacity, print_details=False)
    
    # 错误处理测试
    def test_length_mismatch(self):
        """重量和价值列表长度不一致"""
        weights = [10, 20, 30]
        values = [60, 100]
        with pytest.raises(ValueError, match="重量和价值列表长度不一致"):
            initialize_items(weights, values)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s", "--tb=short"])

