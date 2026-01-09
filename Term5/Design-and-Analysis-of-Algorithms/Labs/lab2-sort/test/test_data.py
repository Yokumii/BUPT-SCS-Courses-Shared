#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from typing import List, Tuple


class TestDataGenerator:
    """测试数据生成器类"""

    # 规模定义
    SMALL_SIZE = 100
    MEDIUM_SIZE = 1000
    LARGE_SIZE = 10000

    @staticmethod
    def generate_random(size: int, seed: int = None) -> List[int]: # type: ignore
        """
        生成完全随机数据
        """
        if seed is not None:
            random.seed(seed)
        return [random.randint(1, size * 10) for _ in range(size)]

    @staticmethod
    def generate_sorted_ascending(size: int) -> List[int]:
        """
        生成升序数据
        """
        return list(range(1, size + 1))

    @staticmethod
    def generate_sorted_descending(size: int) -> List[int]:
        """
        生成降序数据
        """
        return list(range(size, 0, -1))

    @staticmethod
    def generate_duplicates(size: int, unique_count: int = None, seed: int = None) -> List[int]: # pyright: ignore[reportArgumentType]
        """
        生成包含重复元素的数据
        """
        if unique_count is None:
            unique_count = max(10, size // 10)

        if seed is not None:
            random.seed(seed)

        unique_values = list(range(1, unique_count + 1))
        return [random.choice(unique_values) for _ in range(size)]

    @staticmethod
    def generate_all_same(size: int, value: int = 42) -> List[int]:
        """
        生成所有元素相同的数据
        """
        return [value] * size

    @staticmethod
    def get_test_dataset(data_type: str, size: int, **kwargs) -> Tuple[str, List[int]]:
        """
        获取指定类型和规模的测试数据集
        """
        generators = {
            'random': TestDataGenerator.generate_random,
            'ascending': TestDataGenerator.generate_sorted_ascending,
            'descending': TestDataGenerator.generate_sorted_descending,
            'duplicates': TestDataGenerator.generate_duplicates,
            'all_same': TestDataGenerator.generate_all_same,
        }

        if data_type not in generators:
            raise ValueError(f"Unknown data type: {data_type}")

        data = TestDataGenerator._call_generator_safe(generators[data_type], size, **kwargs)
        name = f"{data_type}_{size}"

        return name, data

    @classmethod
    def get_all_test_datasets(cls) -> List[Tuple[str, str, int]]:
        """
        获取所有测试数据集的配置
        """
        sizes = {
            'small': cls.SMALL_SIZE,
            'medium': cls.MEDIUM_SIZE,
            'large': cls.LARGE_SIZE,
        }

        data_types = ['random', 'ascending', 'descending', 'duplicates']

        datasets = []
        for size_name, size_value in sizes.items():
            for data_type in data_types:
                datasets.append((data_type, size_name, size_value))

        return datasets


    @staticmethod
    def _call_generator_safe(generator_func, size: int, **kwargs):
        """安全调用生成器函数，过滤掉不支持的参数"""
        import inspect
        sig = inspect.signature(generator_func)
        valid_kwargs = {}
        for key, value in kwargs.items():
            if key in sig.parameters:
                valid_kwargs[key] = value
        return generator_func(size, **valid_kwargs)


def get_small_datasets():
    """获取小规模测试数据集"""
    return [
        ('random', TestDataGenerator.generate_random(100, seed=42)),
        ('ascending', TestDataGenerator.generate_sorted_ascending(100)),
        ('descending', TestDataGenerator.generate_sorted_descending(100)),
        ('duplicates', TestDataGenerator.generate_duplicates(100, seed=42))
    ]


def get_medium_datasets():
    """获取中规模测试数据集"""
    return [
        ('random', TestDataGenerator.generate_random(1000, seed=42)),
        ('ascending', TestDataGenerator.generate_sorted_ascending(1000)),
        ('descending', TestDataGenerator.generate_sorted_descending(1000)),
        ('duplicates', TestDataGenerator.generate_duplicates(1000, seed=42))
    ]


def get_large_datasets():
    """获取大规模测试数据集"""
    return [
        ('random', TestDataGenerator.generate_random(10000, seed=42)),
        ('ascending', TestDataGenerator.generate_sorted_ascending(10000)),
        ('descending', TestDataGenerator.generate_sorted_descending(10000)),
        ('duplicates', TestDataGenerator.generate_duplicates(10000, seed=42))
    ]
