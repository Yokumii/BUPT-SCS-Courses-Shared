# lab4-knapsack-by-greedy

分数背包问题（贪心法）的实现、测试与性能验证。

## 项目结构

```
.
├── src/
│   └── knapsack.py              # 分数背包贪心实现
├── test/
│   ├── test_cases.py            # 正确性与边界测试（pytest）
│   └── performance_test.py      # 时间复杂度 O(n log n) 验证与绘图
└── docs/
    └── report.pdf / report.typ  # 实验报告
```

## 快速开始

### 环境要求
- Python 3.8+
- pytest

### 安装依赖
```bash
pip install pytest
pip install matplotlib
```

### 运行算法示例
```bash
cd src
python knapsack.py
```

### 运行测试
```bash
cd test
pytest test_cases.py -v -s --tb=short
python performance_test.py
```

