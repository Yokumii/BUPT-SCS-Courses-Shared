# lab3-knapsack-dp

0-1 背包问题（动态规划法）实现、测试与性能验证。

## 项目结构
```
.
├── src/
│   └── knapsack.py              # 0-1 背包 DP 实现（含回溯解向量、1D优化）
├── test/
│   ├── test_cases.py            # 正确性测试
│   └── performance_test.py      # 性能测试
└── docs/
    └── template/report.typ      # 实验报告（Typst）
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

