# lab1-tennis-round-robin-tournament

网球循环赛日程表算法的设计与分析。

## 项目结构/提交材料清单说明

```
.
├── src/                          # 源代码目录
│   ├── divide_tt.py              # 分治法实现
│   ├── backtracking_tt.py        # 回溯法实现
│   └── polygon_tt.py             # 旋转多边形法实现
├── test/                         # 测试用例目录
│   └── test_cases.py             # 综合测试脚本
├── docs/                         # 文档目录
│   ├── report.md                 # 实验报告（Markdown格式）
│   ├── report.pdf                # 实验报告（PDF格式）
│   └── match schedule.xlsx       # 赛程表示例文件
└── README.md                     # 项目说明文件
```

## 快速开始

### 环境要求

- Python 3.8+
- pytest 测试框架
- uv（推荐，用于Python包管理）

### 安装依赖

```bash
# 使用uv安装pytest（推荐）
uv add pytest

# 或使用pip安装
pip install pytest
```

### 运行算法

**分治法实现**：
```bash
cd src
python divide_tt.py
```

**回溯法实现**：
```bash
cd src
python backtracking_tt.py
```

**旋转多边形法实现**：
```bash
cd src
python polygon_tt.py
```

### 运行测试

**运行所有测试用例**：
```bash
cd test
uv run pytest test_cases.py -v -s --tb=short
```

**运行特定测试**：
```bash
cd test
uv run pytest test_cases.py::test_basic_functionality -v
```

### 算法说明

本项目实现了三种不同的循环赛日程表生成算法：

1. **分治法** (`divide_tt.py`)：
   - 时间复杂度：O(n²)
   - 空间复杂度：O(n²)

2. **回溯法** (`backtracking_tt.py`)：
   - 时间复杂度：O(n!)
   - 空间复杂度：O(n²)

3. **旋转多边形法** (`polygon_tt.py`)：
   - 时间复杂度：O(n²)
   - 空间复杂度：O(n²)

### 输出格式说明

所有算法的输出格式统一：

**赛程表格式形如**：
```
   1:  12  11  10   9   8   7   6   5   4   3   2
   2:  11   9   7   5   3  12  10   8   6   4   1
   3:  10   8   6   4   2  11   9   7   5   1  12
   4:   9   7   5   3  12  10   8   6   1   2  11
   5:   8   6   4   2  11   9   7   1   3  12  10
   6:   7   5   3  12  10   8   1   4   2  11   9
   7:   6   4   2  11   9   1   5   3  12  10   8
   8:   5   3  12  10   1   6   4   2  11   9   7
   9:   4   2  11   1   7   5   3  12  10   8   6
  10:   3  12   1   8   6   4   2  11   9   7   5
  11:   2   1   9   7   5   3  12  10   8   6   4
  12:   1  10   8   6   4   2  11   9   7   5   3
```

**输出效果**：
```
请输入选手数量: 12
生成的赛程安排:
（略）
执行时间: 98 微秒
```
