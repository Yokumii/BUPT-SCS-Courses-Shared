#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import copy
from typing import Callable, Optional, List


class SortStatistics:
    """排序统计信息"""
    def __init__(self):
        self.compare_count = 0
        self.move_count = 0
        self.start_time = 0.0
        self.end_time = 0.0

    def reset(self):
        """重置统计信息"""
        self.compare_count = 0
        self.move_count = 0
        self.start_time = 0
        self.end_time = 0

    def get_elapsed_time(self) -> float:
        """获取排序耗时（单位: 秒）"""
        return self.end_time - self.start_time

    def print_statistics(self, algorithm_name: str):
        """打印统计信息"""
        print(f"\n{algorithm_name} 排序统计:")
        print(f"  关键字比较次数: {self.compare_count}")
        print(f"  关键字移动次数: {self.move_count}")
        print(f"  排序时间: {self.get_elapsed_time():.6f} 秒")


class SortingAlgorithms:
    """排序算法模块"""

    def __init__(self):
        self.stats = SortStatistics()

    # ==================== 堆排序 ====================
    def heap_adjust(self, arr: List, root: int, length: int, compare: Callable) -> None:
        """
        调整堆（最大堆）
        """
        temp = arr[root]
        j = 2 * root + 1  # 左子节点

        while j < length:
            # 选择左右子节点中较大的一个
            if j + 1 < length:
                self.stats.compare_count += 1
                if compare(arr[j], arr[j + 1]) < 0:
                    j += 1

            # 如果根节点已经大于等于子节点，则退出
            self.stats.compare_count += 1
            if compare(temp, arr[j]) >= 0:
                break

            # 将子节点移动到根节点位置
            arr[root] = arr[j]
            self.stats.move_count += 1
            root = j
            j = 2 * root + 1

        # 将原根节点值放入最终位置
        arr[root] = temp
        self.stats.move_count += 1

    def heap_sort(self, arr: List, compare: Optional[Callable] = None) -> List:
        """
        堆排序
        """
        # 默认升序
        if compare is None:
            compare = lambda a, b: (a > b) - (a < b)

        self.stats.reset()
        self.stats.start_time = time.time()

        # 复制数组
        result = copy.deepcopy(arr)
        n = len(result)

        # 构建初始最大堆
        for i in range(n // 2 - 1, -1, -1):
            self.heap_adjust(result, i, n, compare)

        # 进行排序操作
        for j in range(n - 1, 0, -1):
            # 交换堆顶和最后一个元素
            result[0], result[j] = result[j], result[0]
            self.stats.move_count += 3  # 一次完整交换计为3次移动

            # 调整剩余元素使其重新满足最大堆
            self.heap_adjust(result, 0, j, compare)

        self.stats.end_time = time.time()
        return result

    # ==================== 归并排序 ====================
    def merge(self, arr: List, left: int, mid: int, right: int, compare: Callable) -> None:
        """
        合并两个有序子数组
        """
        # 创建临时数组存储左右两部分
        left_part = arr[left:mid + 1]
        right_part = arr[mid + 1:right + 1]

        i, j, k = 0, 0, left

        # 合并两个有序数组
        while i < len(left_part) and j < len(right_part):
            self.stats.compare_count += 1
            if compare(left_part[i], right_part[j]) <= 0:
                arr[k] = left_part[i]
                i += 1
            else:
                arr[k] = right_part[j]
                j += 1
            k += 1
            self.stats.move_count += 1

        # 复制左边剩余元素
        while i < len(left_part):
            arr[k] = left_part[i]
            i += 1
            k += 1
            self.stats.move_count += 1

        # 复制右边剩余元素
        while j < len(right_part):
            arr[k] = right_part[j]
            j += 1
            k += 1
            self.stats.move_count += 1

    def merge_sort_recursive(self, arr: List, left: int, right: int, compare: Callable) -> None:
        """
        归并排序递归函数
        """
        if left < right:
            # 分：找到中间位置
            mid = (left + right) // 2

            # 治：递归排序左右两部分
            self.merge_sort_recursive(arr, left, mid, compare)
            self.merge_sort_recursive(arr, mid + 1, right, compare)

            # 合：合并两个有序子数组
            self.merge(arr, left, mid, right, compare)

    def merge_sort(self, arr: List, compare: Optional[Callable] = None) -> List:
        """
        归并排序
        """
        # 默认升序
        if compare is None:
            compare = lambda a, b: (a > b) - (a < b)

        self.stats.reset()
        self.stats.start_time = time.time()

        # 复制数组，避免修改原数组
        result = copy.deepcopy(arr)

        # 调用递归函数进行排序
        if len(result) > 1:
            self.merge_sort_recursive(result, 0, len(result) - 1, compare)

        self.stats.end_time = time.time()
        return result

    # ==================== 快速排序 ====================
    def partition(self, arr: List, low: int, high: int, compare: Callable, use_median_of_three: bool = False) -> int:
        """
        快速排序的划分函数
        """
        if use_median_of_three:
            # 三数取中法选择枢轴
            mid = (low + high) // 2

            # 确保 arr[low] <= arr[mid] <= arr[high]
            if compare(arr[low], arr[mid]) > 0:
                arr[low], arr[mid] = arr[mid], arr[low]
                self.stats.move_count += 3
            if compare(arr[low], arr[high]) > 0:
                arr[low], arr[high] = arr[high], arr[low]
                self.stats.move_count += 3
            if compare(arr[mid], arr[high]) > 0:
                arr[mid], arr[high] = arr[high], arr[mid]
                self.stats.move_count += 3

            # 将中位数放到 low 位置作为枢轴
            arr[low], arr[mid] = arr[mid], arr[low]
            self.stats.move_count += 3

        # 选择第一个元素作为基准
        pivot = arr[low]
        self.stats.move_count += 1

        while low < high:
            # 从右向左找小于基准的元素
            while low < high:
                self.stats.compare_count += 1
                if compare(pivot, arr[high]) <= 0:
                    high -= 1
                else:
                    break

            if low < high:
                arr[low] = arr[high]
                self.stats.move_count += 1

            # 从左向右找大于基准的元素
            while low < high:
                self.stats.compare_count += 1
                if compare(pivot, arr[low]) >= 0:
                    low += 1
                else:
                    break

            if low < high:
                arr[high] = arr[low]
                self.stats.move_count += 1

        # 将基准元素放入最终位置
        arr[low] = pivot
        self.stats.move_count += 1

        return low

    def quick_sort_recursive(self, arr: List, low: int, high: int, compare: Callable, use_median_of_three: bool = False) -> None:
        """
        快速排序递归函数
        """
        while low < high:
            pivot_loc = self.partition(arr, low, high, compare, use_median_of_three)
            # 先处理左子数组
            self.quick_sort_recursive(arr, low, pivot_loc - 1, compare, use_median_of_three)
            # 尾递归优化：右子数组用循环处理
            low = pivot_loc + 1

    def quick_sort(self, arr: List, compare: Optional[Callable] = None, use_median_of_three: bool = False) -> List:
        """
        快速排序
        """
        # 默认升序
        if compare is None:
            compare = lambda a, b: (a > b) - (a < b)

        self.stats.reset()
        self.stats.start_time = time.time()

        # 复制数组，避免修改原数组
        result = copy.deepcopy(arr)

        if len(result) > 1:
            self.quick_sort_recursive(result, 0, len(result) - 1, compare, use_median_of_three)

        self.stats.end_time = time.time()
        return result


def atest():
    # 测试数据
    test_arrays = {
        "随机数组": [64, 34, 25, 12, 22, 11, 90, 88, 45, 50, 23, 36, 18, 77],
        "升序数组": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "降序数组": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        "相同元素": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    }

    sorter = SortingAlgorithms()

    for test_name, test_arr in test_arrays.items():
        print(f"\n{'=' * 60}")
        print(f"测试数据: {test_name}")
        print(f"原始数组: {test_arr}")
        print(f"数组长度: {len(test_arr)}")

        # 堆排序
        result_heap = sorter.heap_sort(test_arr)
        print(f"\n堆排序结果: {result_heap}")
        sorter.stats.print_statistics("堆排序")

        # 归并排序
        result_merge = sorter.merge_sort(test_arr)
        print(f"\n归并排序结果: {result_merge}")
        sorter.stats.print_statistics("归并排序")

        # 快速排序
        result_quick = sorter.quick_sort(test_arr)
        print(f"\n快速排序结果: {result_quick}")
        sorter.stats.print_statistics("快速排序")


if __name__ == "__main__":
    atest()
