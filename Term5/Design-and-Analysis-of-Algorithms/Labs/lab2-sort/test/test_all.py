#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import sys
import os
import copy

# 增加递归深度限制
sys.setrecursionlimit(50000)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from sorting_algorithms import SortingAlgorithms
from test_data import TestDataGenerator


class TestAllSortingAlgorithms:
    """排序算法统一测试类"""

    @pytest.fixture
    def sorter(self):
        """创建排序器实例"""
        return SortingAlgorithms()

    def validate_sorted(self, original: list, result: list) -> bool:
        """验证排序结果的正确性"""
        if len(original) != len(result):
            return False
        if sorted(original) != sorted(result):
            return False
        for i in range(len(result) - 1):
            if result[i] > result[i + 1]:
                return False
        return True

    def run_test(self, sorter, algorithm: str, data_type: str, size: int, seed: int = 42):
        """
        运行单个测试
        """
        # 生成测试数据
        if data_type == 'random':
            data = TestDataGenerator.generate_random(size, seed=seed)
        elif data_type == 'ascending':
            data = TestDataGenerator.generate_sorted_ascending(size)
        elif data_type == 'descending':
            data = TestDataGenerator.generate_sorted_descending(size)
        elif data_type == 'duplicates':
            data = TestDataGenerator.generate_duplicates(size, seed=seed)
        elif data_type == 'all_same':
            data = TestDataGenerator.generate_all_same(size)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        original = copy.deepcopy(data)

        # 执行排序
        if algorithm == 'heap_sort':
            result = sorter.heap_sort(data)
        elif algorithm == 'merge_sort':
            result = sorter.merge_sort(data)
        elif algorithm == 'quick_sort':
            result = sorter.quick_sort(data, use_median_of_three=False)
        elif algorithm == 'quick_sort_optimized':
            result = sorter.quick_sort(data, use_median_of_three=True)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        # 验证正确性
        is_valid = self.validate_sorted(original, result)

        # 获取统计信息
        compare_count = sorter.stats.compare_count
        move_count = sorter.stats.move_count
        time_ms = (sorter.stats.end_time - sorter.stats.start_time) * 1000

        # 打印结果
        status = "✓" if is_valid else "✗"
        print(f"\n{status} {algorithm:25} | {data_type:15} | n={size:6,} | "
              f"比较={compare_count:10,} | 移动={move_count:10,} | 时间={time_ms:8.3f}ms")

        return {
            'algorithm': algorithm,
            'data_type': data_type,
            'size': size,
            'valid': is_valid,
            'compare': compare_count,
            'move': move_count,
            'time': time_ms
        }

    # ==================== 小规模测试 (100) ====================

    @pytest.mark.parametrize("algorithm", ['heap_sort', 'merge_sort', 'quick_sort'])
    @pytest.mark.parametrize("data_type", ['random', 'ascending', 'descending', 'duplicates', 'all_same'])
    def test_small_scale(self, sorter, algorithm, data_type):
        """小规模测试 (n=100)"""
        result = self.run_test(sorter, algorithm, data_type, 100)
        assert result['valid'], f"{algorithm} 在 {data_type} 数据上排序失败"

    # ==================== 中规模测试 (1000) ====================

    @pytest.mark.parametrize("algorithm", ['heap_sort', 'merge_sort', 'quick_sort'])
    @pytest.mark.parametrize("data_type", ['random', 'ascending', 'descending', 'duplicates', 'all_same'])
    def test_medium_scale(self, sorter, algorithm, data_type):
        """中规模测试 (n=1000)"""
        result = self.run_test(sorter, algorithm, data_type, 1000)
        assert result['valid'], f"{algorithm} 在 {data_type} 数据上排序失败"

    # ==================== 大规模测试 (10000) ====================

    @pytest.mark.parametrize("algorithm", ['heap_sort', 'merge_sort', 'quick_sort'])
    @pytest.mark.parametrize("data_type", ['random', 'ascending', 'descending', 'duplicates', 'all_same'])
    def test_large_scale(self, sorter, algorithm, data_type):
        """大规模测试 (n=10000)"""
        result = self.run_test(sorter, algorithm, data_type, 10000)
        assert result['valid'], f"{algorithm} 在 {data_type} 数据上排序失败"

    # ==================== 快速排序退化测试 ====================

    @pytest.mark.parametrize("size", [100, 500, 1000])
    def test_quick_sort_degradation(self, sorter, size):
        """快速排序退化对比测试"""
        print(f"\n{'='*80}")
        print(f"快速排序退化对比 (升序数据, n={size:,})")
        print(f"{'='*80}")

        # 基础版本（会退化）
        result_basic = self.run_test(sorter, 'quick_sort', 'ascending', size)

        # 优化版本（不退化）
        result_opt = self.run_test(sorter, 'quick_sort_optimized', 'ascending', size)

        # 性能对比
        if result_opt['compare'] > 0:
            compare_ratio = result_basic['compare'] / result_opt['compare']
            time_ratio = result_basic['time'] / result_opt['time']

            print(f"\n性能对比:")
            print(f"  比较次数: 基础版 {result_basic['compare']:,} vs 优化版 {result_opt['compare']:,} = {compare_ratio:.1f}x")
            print(f"  执行时间: 基础版 {result_basic['time']:.3f}ms vs 优化版 {result_opt['time']:.3f}ms = {time_ratio:.1f}x")

        assert result_basic['valid'], "基础版本排序失败"
        assert result_opt['valid'], "优化版本排序失败"

    # ==================== 边界情况测试 ====================

    def test_empty_array(self, sorter):
        """空数组测试"""
        data = []
        for algo in ['heap_sort', 'merge_sort', 'quick_sort']:
            func = getattr(sorter, algo)
            result = func(data)
            assert result == [], f"{algo} 空数组测试失败"

    def test_single_element(self, sorter):
        """单元素测试"""
        data = [42]
        for algo in ['heap_sort', 'merge_sort', 'quick_sort']:
            func = getattr(sorter, algo)
            result = func(data)
            assert result == [42], f"{algo} 单元素测试失败"

    def test_two_elements(self, sorter):
        """两元素测试"""
        data = [2, 1]
        for algo in ['heap_sort', 'merge_sort', 'quick_sort']:
            func = getattr(sorter, algo)
            result = func(data)
            assert result == [1, 2], f"{algo} 两元素测试失败"


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-s", "--tb=short"])
