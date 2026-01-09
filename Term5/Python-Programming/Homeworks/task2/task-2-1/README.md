# 链家新房爬虫

## 项目说明

本项目用于爬取链家网（北京）新房数据，完成数据预处理和统计分析。

## 功能特性

- ✅ 新房数据爬取（名称、类别、位置、房型、面积、均价、总价）
- ✅ Cookie管理和半自动登录
- ✅ 代理池支持
- ✅ 数据预处理（去空格、删除面积缺失数据）
- ✅ 统计分析（总价/均价的最大值、最小值、中位数）

## 环境要求

- Python >= 3.8
- Chrome浏览器（用于自动登录）

## 安装依赖

使用 uv（推荐）:
```bash
uv sync
```

或使用 pip:
```bash
pip install -r requirements.txt
```

## 使用方法

1. 进入src目录:
```bash
cd src
```

2. 运行爬虫:
```bash
uv run python main.py
# 或
python main.py
```

3. 首次运行会自动打开浏览器，请手动完成登录
4. 登录成功后Cookie会自动保存，下次运行无需重新登录
5. 爬取完成后会自动进行数据预处理和统计分析

## 输出文件

- `data/lianjia_loupan_raw.csv` - 原始爬取数据
- `data/lianjia_loupan_processed.csv` - 预处理后数据
- `data/failed_pages/` - 失败页面保存目录（用于调试）

## 项目结构

```
task-2-1/
├── src/
│   ├── config.py           # 配置文件
│   ├── cookie_manager.py   # Cookie管理
│   ├── auto_login.py       # 自动登录
│   ├── proxy_pool.py       # 代理池
│   ├── crawler.py          # 爬虫核心
│   ├── data_processor.py   # 数据处理
│   └── main.py            # 主程序
├── data/                   # 数据目录
├── pyproject.toml         # 依赖配置
└── README.md              # 说明文档
```

## 注意事项

1. 爬取间隔默认为2秒，避免触发反爬机制
2. 如遇Cookie失效，程序会提示重新登录
3. 代理池功能可选，建议使用稳定的代理服务
