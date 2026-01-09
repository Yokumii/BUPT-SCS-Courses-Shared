# -*- coding: utf-8 -*-
"""
链家新房爬虫配置文件
"""

# 基础URL
BASE_URL = "https://bj.fang.lianjia.com/loupan/"

# 爬取页数（新房不按城区划分，总共277条数据分布在18页）
MAX_PAGES = 18

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer": "https://bj.fang.lianjia.com/loupan/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 请求间隔（秒），避免触发反爬
REQUEST_DELAY = 2.0

# 连续失败阈值，超过此值则停止爬取
MAX_CONSECUTIVE_FAILURES = 3

# 单页重试次数
PAGE_RETRY_COUNT = 3

# 重试间隔（秒）
RETRY_DELAY = 3.0

# 失败页面保存目录
FAILED_PAGES_DIR = "../data/failed_pages"

# 输出文件路径
OUTPUT_FILE = "../data/lianjia_loupan_raw.csv"
PROCESSED_FILE = "../data/lianjia_loupan_processed.csv"

# CSV列名（原始数据）
CSV_COLUMNS = ["名称", "类别", "地理位置-区", "地理位置-板块", "地理位置-详细地址",
               "房型", "面积", "均价", "总价"]
