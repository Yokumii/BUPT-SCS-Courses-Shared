#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import math
import random

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from knapsack import knapsack  # noqa: E402


def generate_weights_values(n, max_weight=120, max_value=200):
    """生成权值与价值，不绑定容量。"""
    weights = [random.randint(1, max_weight) for _ in range(n)]
    values = [random.randint(1, max_value) for _ in range(n)]
    return weights, values


def measure_time(weights, values, capacity, iterations=3):
    """
    多次运行取平均时间（秒）
    """
    durations = []
    for _ in range(iterations):
        start = time.perf_counter()
        knapsack(weights, values, capacity)
        end = time.perf_counter()
        durations.append(end - start)
    return sum(durations) / len(durations)


def verify_complexity():

    # 固定较小 W，增加 n
    fixed_capacity = 200
    test_ns = [50, 100, 200, 400, 800]
    results_n = []

    print("\n固定较小 W，增加 n")
    print(f"{'n':<8} {'W(容量)':<12} {'n*W':<14} {'T(n) ms':<14} {'T(n)/(n*W)':<18} {'增长倍数(实/理)':<24}")
    print("-" * 100)

    prev_time = None
    prev_nw = None
    for n in test_ns:
        weights, values = generate_weights_values(n)
        avg_time = measure_time(weights, values, fixed_capacity, iterations=3)
        avg_ms = avg_time * 1000
        nw = n * fixed_capacity
        ratio = avg_ms / nw if nw > 0 else 0

        if prev_time is not None and prev_nw is not None:
            theoretical = nw / prev_nw
            actual = avg_ms / prev_time if prev_time > 0 else 0
            growth_info = f"{actual:.2f}x / {theoretical:.2f}x"
        else:
            growth_info = "-"

        results_n.append({
            "n": n,
            "capacity": fixed_capacity,
            "nw": nw,
            "time_ms": avg_ms,
            "ratio": ratio,
            "growth": growth_info,
        })

        print(f"{n:<8} {fixed_capacity:<12} {nw:<14} {avg_ms:<14.3f} {ratio:<18.6f} {growth_info:<24}")

        prev_time = avg_ms
        prev_nw = nw

    # 固定 n，放大 W
    fixed_n = 100
    capacities = [100, 1000, 10000, 100000, 1000000]
    results_w = []

    print("\n固定 n=100，放大 W")
    print(f"{'n':<8} {'W(容量)':<12} {'n*W':<14} {'T(n) ms':<14} {'T(n)/(n*W)':<18} {'增长倍数(实/理)':<24}")
    print("-" * 100)

    prev_time = None
    prev_nw = None
    weights_w, values_w = generate_weights_values(fixed_n)
    for cap in capacities:
        avg_time = measure_time(weights_w, values_w, cap, iterations=3)
        avg_ms = avg_time * 1000
        nw = fixed_n * cap
        ratio = avg_ms / nw if nw > 0 else 0

        if prev_time is not None and prev_nw is not None:
            theoretical = nw / prev_nw
            actual = avg_ms / prev_time if prev_time > 0 else 0
            growth_info = f"{actual:.2f}x / {theoretical:.2f}x"
        else:
            growth_info = "-"

        results_w.append({
            "n": fixed_n,
            "capacity": cap,
            "nw": nw,
            "time_ms": avg_ms,
            "ratio": ratio,
            "growth": growth_info,
        })

        print(f"{fixed_n:<8} {cap:<12} {nw:<14} {avg_ms:<14.3f} {ratio:<18.6f} {growth_info:<24}")

        prev_time = avg_ms
        prev_nw = nw

    return results_n, results_w


def plot_complexity(results=None):

    try:
        import matplotlib.pyplot as plt
        import matplotlib

        if results is None:
            results = verify_complexity()
        results_n, results_w = results

        # 中文字体（macOS 常见字体）
        chinese_fonts = ['PingFang SC', 'STHeiti', 'Arial Unicode MS', 'Heiti SC', 'SimHei']
        matplotlib.rcParams['font.sans-serif'] = chinese_fonts
        matplotlib.rcParams['axes.unicode_minus'] = False

        # 图1：固定 W，n 增长
        ns = [r["n"] for r in results_n]
        times_n = [r["time_ms"] for r in results_n]
        nws_n = [r["nw"] for r in results_n]

        plt.figure(figsize=(10, 4.5))
        plt.plot(ns, times_n, "o-", label="实际时间 T(n)")
        if nws_n and nws_n[0] != 0:
            scale = times_n[0] / nws_n[0]
            plt.plot(ns, [scale * x for x in nws_n], "--", label=f"拟合: {scale:.6f}·(n·W)")
        plt.xlabel("n")
        plt.ylabel("时间 (ms)")
        plt.title("固定小容量 W，n 增长")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("complexity_verification_dp_n.png", dpi=300, bbox_inches="tight")
        print("\n已生成图表: complexity_verification_dp_n.png")

        # 图2：固定 n，W 增长
        caps = [r["capacity"] for r in results_w]
        times_w = [r["time_ms"] for r in results_w]
        nws_w = [r["nw"] for r in results_w]

        plt.figure(figsize=(10, 4.5))
        plt.plot(caps, times_w, "o-", label="实际时间 T(n)")
        if nws_w and nws_w[0] != 0:
            scale = times_w[0] / nws_w[0]
            plt.plot(caps, [scale * x for x in nws_w], "--", label=f"拟合: {scale:.6f}·(n·W)")
        plt.xlabel("W (容量)")
        plt.ylabel("时间 (ms)")
        plt.title("固定 n=100，容量 W 增长")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig("complexity_verification_dp_w.png", dpi=300, bbox_inches="tight")
        print("已生成图表: complexity_verification_dp_w.png")
    except ImportError:
        print("\n未安装 matplotlib，跳过绘图")


if __name__ == "__main__":
    random.seed(42)
    results = verify_complexity()
    plot_complexity(results)

