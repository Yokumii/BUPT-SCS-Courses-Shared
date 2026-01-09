# -*- coding: utf-8 -*-
"""
链家爬虫配置文件
"""

# 基础URL
BASE_URL = "https://bj.lianjia.com/ershoufang/"

# 城区映射：城区名 -> URL路径
DISTRICTS = {
    "东城": "dongcheng",
    "西城": "xicheng",
    "海淀": "haidian",
    "朝阳": "chaoyang",
}

# 每个城区爬取页数
PAGES_PER_DISTRICT = 3

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer": "https://bj.lianjia.com/ershoufang/",
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
OUTPUT_FILE = "../data/lianjia_ershoufang.csv"

# CSV列名
CSV_COLUMNS = ["城区", "房源编号", "小区名称", "平米数（单位：平米）", "总价(单位：万)", "单价(单位：元/平)"]
