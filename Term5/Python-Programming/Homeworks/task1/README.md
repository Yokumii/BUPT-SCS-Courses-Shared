# 链家二手房爬虫

爬取北京链家官网东城、西城、海淀、朝阳四个城区的二手房数据。

## 项目结构

```
.
├── data/                       # 数据目录
│   ├── failed_pages/           # 失败页面保存目录
│   └── lianjia_ershoufang.csv  # 爬取结果数据文件
│
├── docs/                       # 文档目录
│   └── report.md               # 实验报告
│
├── src/                        # 源代码目录
│   ├── main.py                 # 主程序入口
│   ├── crawler.py              # 爬虫核心逻辑
│   ├── config.py               # 配置文件
│   ├── cookie_manager.py       # Cookie管理模块
│   ├── auto_login.py           # 半自动登录模块
│   ├── proxy_pool.py           # 代理池管理模块
│   ├── cookies.json            # Cookie存储文件
│   └── proxy_pool.json         # 代理池配置文件
│
├── pyproject.toml              # 项目依赖配置（uv）
├── uv.lock                     # 依赖锁定文件
└── README.md                   # 项目说明
```

## 环境配置

本项目使用 [uv](https://github.com/astral-sh/uv) 进行 Python 包管理。

```bash
# 安装依赖
uv sync
```

## 快速开始

### 运行爬虫

```bash
cd src
uv run python main.py
```

### 运行流程

```
启动程序
    ↓
检查Cookie → 不存在 → 启动半自动登录 → 用户手动完成验证 → 保存Cookie
    ↓ 存在
询问是否使用代理
    ↓
开始爬取（4城区 × 3页）
    ↓
保存数据到 data/lianjia_ershoufang.csv
```

## 模块说明

| 模块 | 功能 |
|------|------|
| `main.py` | 主程序入口，协调各模块 |
| `crawler.py` | 爬虫核心：页面获取、数据解析、CSV存储 |
| `config.py` | 配置管理：URL、请求头、爬取参数 |
| `cookie_manager.py` | Cookie的JSON文件读写 |
| `auto_login.py` | Selenium半自动登录，获取Cookie |
| `proxy_pool.py` | IP代理池管理，支持多种选择策略 |

## 配置说明

在 `config.py` 中可调整以下参数：

```python
# 爬取范围
DISTRICTS = {"东城": "dongcheng", "西城": "xicheng", ...}
PAGES_PER_DISTRICT = 3          # 每个城区爬取页数

# 反爬策略
REQUEST_DELAY = 2.0             # 请求间隔（秒）
PAGE_RETRY_COUNT = 3            # 单页重试次数
MAX_CONSECUTIVE_FAILURES = 3    # 连续失败阈值

# 输出路径
OUTPUT_FILE = "../data/lianjia_ershoufang.csv"
```

## 输出格式

数据保存在 `data/lianjia_ershoufang.csv`，包含以下字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| 城区 | 所属城区 | 海淀 |
| 房源编号 | 房源唯一ID | 101123456789 |
| 小区名称 | 小区名称 | 万柳书院 |
| 平米数（单位：平米） | 建筑面积 | 89.3 |
| 总价(单位：万) | 总价 | 1280 |
| 单价(单位：元/平) | 单价 | 65123 |

## 代理池使用（可选）

编辑 `src/proxy_pool.json` 配置代理：

```json
{
  "proxies": [
    {
      "name": "代理1",
      "host": "your-proxy-ip",
      "port": 8888,
      "type": "http",
      "enabled": true
    }
  ]
}
```

支持的代理选择策略：
- `round_robin` - 轮询（默认）
- `random` - 随机选择
- `least_used` - 最少使用优先
- `best_performance` - 成功率最高优先

注意：同账号不同 IP 访问可能触发风控，建议谨慎使用。
