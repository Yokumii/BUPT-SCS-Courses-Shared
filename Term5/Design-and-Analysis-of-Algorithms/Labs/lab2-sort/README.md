# lab2-sort

三种排序算法的设计与分析。

## 项目结构/提交材料清单说明

```
.
├── src/                          # 源代码目录
│   └── sorting_algorithms.py     # 算法模块
├── test/                         # 测试用例目录
│   ├── test_data.py              # 测试数据生成器
│   └── test_all.py               # 综合测试脚本
├── docs/                         # 文档目录
│   ├── report.md                 # 实验报告（Markdown格式）
│   └── report.pdf                # 实验报告（PDF格式）
└── README.md                     # 项目说明文件
```

## 快速开始

### 环境要求

- Python 3.8+
- pytest 测试框架
- uv（推荐，用于Python包管理）

### 运行测试

```bash
# python 环境配置
uv venv
source .venv/bin/activate
uv pip install pytest

# 运行算法程序
python src/sorting_algorithms.py

# 运行测试程序
pytest test/test_all.py -v -s
```