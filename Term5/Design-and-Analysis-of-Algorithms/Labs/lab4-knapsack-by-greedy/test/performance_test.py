#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import math
import random

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from knapsack import initialize_items, knapsack


def generate_test_data(n):
    """
    生成测试数据
    """
    weights = [random.randint(1, 100) for _ in range(n)]
    values = [random.randint(1, 200) for _ in range(n)]
    
    total_weight = sum(weights)
    capacity = int(total_weight * 0.6)
    
    return weights, values, capacity


def measure_time(weights, values, capacity, iterations=10):
    """
    测量算法执行时间（多次运行取平均）
    """
    times = []
    
    for _ in range(iterations):
        items = initialize_items(weights.copy(), values.copy())
        
        start_time = time.perf_counter()
        knapsack(items, capacity)
        end_time = time.perf_counter()
        
        times.append(end_time - start_time)
    
    return sum(times) / len(times)


def verify_complexity():
    
    # 测试规模（从小到大）
    test_sizes = [100, 200, 500, 1000, 2000, 5000, 10000]
    
    results = []
    
    print(f"\n{'规模(n)':<10} {'时间T(n)(ms)':<15} {'n*log(n)':<15} {'T(n)/(n*log(n))':<20} {'增长倍数':<15}")
    print("-" * 80)
    
    prev_time = None
    prev_n = None
    
    for n in test_sizes:
        # 生成测试数据
        weights, values, capacity = generate_test_data(n)
        
        # 测量执行时间（运行5次取平均）
        avg_time = measure_time(weights, values, capacity, iterations=5)
        avg_time_ms = avg_time * 1000  # 转换为毫秒
        
        # 计算 n * log(n)
        n_log_n = n * math.log2(n)
        
        # 计算比值
        ratio = avg_time_ms / n_log_n if n_log_n > 0 else 0
        
        # 计算增长倍数（与上一个规模相比）
        if prev_time is not None:
            # 理论增长倍数：T(2n) / T(n) ≈ (2n * log(2n)) / (n * log(n)) = 2 * (1 + log(2)/log(n))
            theoretical_ratio = (n * math.log2(n)) / (prev_n * math.log2(prev_n))
            actual_ratio = avg_time_ms / prev_time if prev_time > 0 else 0
            growth_info = f"{actual_ratio:.2f}x (理论: {theoretical_ratio:.2f}x)"
        else:
            growth_info = "-"
        
        results.append({
            'n': n,
            'time_ms': avg_time_ms,
            'n_log_n': n_log_n,
            'ratio': ratio,
            'growth': growth_info
        })
        
        print(f"{n:<10} {avg_time_ms:<15.4f} {n_log_n:<15.2f} {ratio:<20.6f} {growth_info:<15}")
        
        prev_time = avg_time_ms
        prev_n = n
    
    return results


def plot_complexity_verification(results=None):
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        import numpy as np
        
        # 配置中文字体支持（macOS）
        chinese_fonts = ['PingFang SC', 'STHeiti', 'Arial Unicode MS', 'Heiti SC', 'SimHei']
        
        # 设置 matplotlib 使用中文字体
        plt.rcParams['font.sans-serif'] = chinese_fonts
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 如果没有传入结果，则运行验证
        if results is None:
            results = verify_complexity()
        
        ns = [r['n'] for r in results]
        times = [r['time_ms'] for r in results]
        n_log_n = [r['n_log_n'] for r in results]
        
        plt.figure(figsize=(12, 5))
        
        plt.plot(ns, times, 'o-', label='实际时间 T(n)', linewidth=2, markersize=8)
        plt.plot(ns, [t * results[0]['ratio'] for t in n_log_n], '--', 
                label=f"拟合曲线 (比例: {results[0]['ratio']:.6f})", linewidth=2)
        plt.xlabel('规模 n', fontsize=12)
        plt.ylabel('执行时间 (ms)', fontsize=12)
        plt.title('实际时间 vs n*log(n) 拟合', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.savefig('complexity_verification.png', dpi=300, bbox_inches='tight')
        print("\n图表已保存为 complexity_verification.png")
        
    except ImportError:
        print("\n注意：未安装 matplotlib，跳过图表绘制")



if __name__ == "__main__":
    # 设置随机种子以确保可重复性
    random.seed(42)
    
    # 运行验证
    results = verify_complexity()
    
    # 尝试绘制图表（可选）
    try:
        plot_complexity_verification(results)
    except Exception as e:
        print(f"\n绘制图表时出错: {e}")
        pass

