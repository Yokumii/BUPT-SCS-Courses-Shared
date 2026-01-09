# -*- coding: utf-8 -*-
"""
新房爬虫主程序
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import os
from datetime import datetime
from config import (
    BASE_URL, MAX_PAGES,
    HEADERS, REQUEST_DELAY, OUTPUT_FILE, CSV_COLUMNS,
    MAX_CONSECUTIVE_FAILURES, FAILED_PAGES_DIR,
    PAGE_RETRY_COUNT, RETRY_DELAY
)
from cookie_manager import load_cookies_from_file
from proxy_pool import ProxyPool, fetch_with_proxy


def build_url(page: int) -> str:
    """
    构建目标URL

    Args:
        page: 页码，从1开始

    Returns:
        完整的URL字符串
    """
    if page == 1:
        return BASE_URL
    return f"{BASE_URL}pg{page}/"


def parse_room_type(room_text: str) -> str:
    """
    从房型文本中提取最小房型

    Args:
        room_text: 房型文本，如 "2室 3室" 或 "2居"

    Returns:
        最小房型，如 "2室" 或 "2居"
    """
    # 匹配所有房型（如 "2室"、"3室"、"2居"等）
    matches = re.findall(r'(\d+[室居])', room_text)
    if matches:
        # 提取数字并找到最小值
        min_room = min(matches, key=lambda x: int(re.search(r'\d+', x).group()))
        return min_room
    return ""


def parse_area(area_text: str) -> str:
    """
    从面积文本中提取中值并取整

    Args:
        area_text: 面积文本，如 "建面 65-117㎡" 或 "建面 360㎡"

    Returns:
        面积中值（取整），如 "91" 或 "360"
    """
    # 匹配区间：如 "65-117"
    range_match = re.search(r'(\d+)-(\d+)', area_text)
    if range_match:
        min_val = int(range_match.group(1))
        max_val = int(range_match.group(2))
        mid_val = (min_val + max_val) // 2
        return str(mid_val)

    # 匹配单个数值：如 "360㎡"
    single_match = re.search(r'(\d+)', area_text)
    if single_match:
        return single_match.group(1)

    return ""


def parse_total_price(price_text: str) -> str:
    """
    从总价文本中提取中值并取整

    Args:
        price_text: 总价文本，如 "总价275-404万/套" 或 "总价300万"

    Returns:
        总价中值（取整），如 "340" 或 "300"
    """
    # 匹配区间：如 "275-404"
    range_match = re.search(r'(\d+)-(\d+)', price_text)
    if range_match:
        min_val = int(range_match.group(1))
        max_val = int(range_match.group(2))
        mid_val = (min_val + max_val) // 2
        return str(mid_val)

    # 匹配单个数值：如 "300"
    single_match = re.search(r'(\d+)', price_text)
    if single_match:
        return single_match.group(1)

    return ""


def save_failed_page(html: str, url: str, reason: str, status_code: int = None):
    """
    保存失败的页面到本地，便于分析

    Args:
        html: 页面HTML内容
        url: 请求的URL
        reason: 失败原因
        status_code: HTTP状态码（如有）
    """
    os.makedirs(FAILED_PAGES_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 从URL中提取页码
    url_part = url.replace(BASE_URL, "").replace("/", "_").strip("_") or "index"
    filename = f"{timestamp}_{url_part}.html"
    filepath = os.path.join(FAILED_PAGES_DIR, filename)

    # 添加调试信息
    debug_info = f"""<!--
失败页面调试信息
================
URL: {url}
时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
状态码: {status_code or "N/A"}
失败原因: {reason}
================
-->
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(debug_info + (html or "<!-- 页面内容为空 -->"))

    print(f"  ⚠️ 失败页面已保存: {filepath}")


def fetch_page_with_retry(url: str, cookies: dict = None, proxy_pool: ProxyPool = None) -> tuple:
    """
    带重试机制的页面获取

    Args:
        url: 目标URL
        cookies: 可选的cookies字典
        proxy_pool: 可选的代理池实例

    Returns:
        (页面HTML内容, HTTP状态码, 错误信息, 重试次数)
    """
    last_html, last_status, last_error = "", None, None

    for attempt in range(PAGE_RETRY_COUNT + 1):
        html, status_code, error = fetch_page(url, cookies, proxy_pool)

        # 请求成功且状态码正常
        if status_code == 200 and html:
            return html, status_code, None, attempt

        # 记录最后一次的结果
        last_html, last_status, last_error = html, status_code, error

        # 如果还有重试机会
        if attempt < PAGE_RETRY_COUNT:
            print(f"    ↻ 第 {attempt + 1} 次重试（等待 {RETRY_DELAY} 秒）...")
            time.sleep(RETRY_DELAY)

    # 所有重试都失败
    return last_html, last_status, last_error, PAGE_RETRY_COUNT


def fetch_page(url: str, cookies: dict = None, proxy_pool: ProxyPool = None) -> tuple:
    """
    获取页面HTML内容（支持代理池）

    Args:
        url: 目标URL
        cookies: 可选的cookies字典
        proxy_pool: 可选的代理池实例

    Returns:
        (页面HTML内容, HTTP状态码, 错误信息)
    """
    try:
        if proxy_pool:
            # 使用代理池
            response = fetch_with_proxy(
                url,
                proxy_pool,
                headers=HEADERS,
                cookies=cookies,
                timeout=10,
                max_retries=3
            )
            if response:
                return response.text, response.status_code, None
            else:
                return "", None, "代理池请求失败"
        else:
            # 直连
            response = requests.get(url, headers=HEADERS, cookies=cookies, timeout=10)
            return response.text, response.status_code, None
    except requests.RequestException as e:
        return "", None, str(e)


def parse_page(html: str) -> list:
    """
    解析页面，提取楼盘数据

    Args:
        html: 页面HTML内容

    Returns:
        楼盘数据列表，每个元素为字典
    """
    loupans = []
    soup = BeautifulSoup(html, 'html.parser')

    # 查找楼盘列表容器
    list_wrapper = soup.select_one('ul.resblock-list-wrapper')
    if not list_wrapper:
        print("  ⚠️ 未找到楼盘列表容器")
        return loupans

    # 遍历每个楼盘项
    for item in list_wrapper.select('li'):
        try:
            loupan = {}

            # 1. 楼盘名称
            name_elem = item.select_one('.resblock-name a.name')
            loupan['名称'] = name_elem.text.strip() if name_elem else ""

            # 2. 楼盘类别
            type_elem = item.select_one('.resblock-type')
            loupan['类别'] = type_elem.text.strip() if type_elem else ""

            # 3. 地理位置（3个字段：2个span + 1个a标签）
            location_spans = item.select('.resblock-location span')
            location_link = item.select_one('.resblock-location a')

            # 区和板块（2个span）
            if len(location_spans) >= 2:
                loupan['地理位置-区'] = location_spans[0].text.strip()
                loupan['地理位置-板块'] = location_spans[1].text.strip()
            else:
                loupan['地理位置-区'] = ""
                loupan['地理位置-板块'] = ""

            # 详细地址（a标签）
            loupan['地理位置-详细地址'] = location_link.text.strip() if location_link else ""

            # 4. 房型（取最小房型）
            room_elem = item.select_one('.resblock-room span')
            if room_elem:
                loupan['房型'] = parse_room_type(room_elem.text)
            else:
                loupan['房型'] = ""

            # 5. 面积（区间取中值并取整）
            area_elem = item.select_one('.resblock-area span')
            if area_elem:
                loupan['面积'] = parse_area(area_elem.text)
            else:
                loupan['面积'] = ""

            # 6. 均价
            price_elem = item.select_one('.main-price span.number')
            loupan['均价'] = price_elem.text.strip() if price_elem else ""

            # 7. 总价（区间取中值并取整）
            total_price_elem = item.select_one('.second')
            if total_price_elem:
                loupan['总价'] = parse_total_price(total_price_elem.text)
            else:
                loupan['总价'] = ""

            # 只添加有名称的楼盘
            if loupan['名称']:
                loupans.append(loupan)

        except Exception as e:
            print(f"  ⚠️ 解析楼盘项失败: {e}")
            continue

    return loupans


def save_to_csv(data: list, filepath: str):
    """
    保存数据到CSV文件

    Args:
        data: 楼盘数据列表
        filepath: 输出文件路径
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(data)

    print(f"✓ 数据已保存到: {filepath}")


def crawl(cookies: dict = None, use_proxy: bool = False) -> tuple:
    """
    执行爬虫主逻辑

    Args:
        cookies: 可选的cookies字典，用于登录态
        use_proxy: 是否使用代理池

    Returns:
        (楼盘数据列表, 是否需要重新登录)
    """
    all_loupans = []
    consecutive_failures = 0
    total_failures = 0
    need_relogin = False

    # 初始化代理池
    proxy_pool = None
    if use_proxy:
        print("\n初始化代理池...")
        proxy_pool = ProxyPool()
        if proxy_pool.proxies:
            print(f"代理池已就绪，共 {len(proxy_pool.proxies)} 个代理")
        else:
            print("⚠️ 代理池为空，将使用直连")
            use_proxy = False

    print(f"\n开始爬取新房数据（预计 {MAX_PAGES} 页）")

    for page in range(1, MAX_PAGES + 1):
        url = build_url(page)

        proxy_info = ""
        if use_proxy and proxy_pool:
            proxy_info = " [使用代理]"

        print(f"\n正在爬取第 {page} 页{proxy_info}: {url}")

        html, status_code, error, retries = fetch_page_with_retry(url, cookies, proxy_pool if use_proxy else None)

        # 显示重试信息
        if retries > 0 and status_code == 200:
            print(f"  ✓ 第 {retries + 1} 次尝试成功")

        # 检查HTTP状态码
        if status_code and status_code != 200:
            reason = f"HTTP状态码错误: {status_code}"
            print(f"  ❌ {reason}")
            save_failed_page(html, url, reason, status_code)
            consecutive_failures += 1
            total_failures += 1

            # 检查是否可能是Cookie失效
            if status_code in [302, 403, 401]:
                print(f"  ⚠️ 状态码 {status_code} 可能表示Cookie已失效")
                need_relogin = True

        elif error:
            reason = f"请求错误: {error}"
            print(f"  ❌ {reason}")
            save_failed_page(html, url, reason)
            consecutive_failures += 1
            total_failures += 1

        elif not html:
            reason = "获取到空页面"
            print(f"  ❌ {reason}")
            save_failed_page("", url, reason)
            consecutive_failures += 1
            total_failures += 1

        else:
            # 解析页面
            loupans = parse_page(html)

            if not loupans:
                # 获取到页面但没有解析出数据
                reason = "未解析到楼盘数据（可能已无更多数据或Cookie失效）"
                print(f"  ⚠️ {reason}")
                save_failed_page(html, url, reason, status_code)
                consecutive_failures += 1
                total_failures += 1

                # 如果是首页就没数据，很可能是Cookie失效
                if page == 1:
                    print(f"  ⚠️ 首页无数据，Cookie可能已失效")
                    need_relogin = True
            else:
                # 成功获取数据，重置连续失败计数
                all_loupans.extend(loupans)
                print(f"  ✓ 获取到 {len(loupans)} 条楼盘数据")
                consecutive_failures = 0

        # 检查是否需要停止爬取
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            print(f"\n❌ 连续失败 {consecutive_failures} 次，停止爬取")

            if need_relogin:
                print(f"  ⚠️ 检测到可能的Cookie失效，建议重新登录获取Cookie")

            # 保存已获取的数据
            if all_loupans:
                save_to_csv(all_loupans, OUTPUT_FILE)
                print(f"\n已保存 {len(all_loupans)} 条已获取的数据")

            return all_loupans, need_relogin

        # 请求间隔，避免触发反爬
        if page < MAX_PAGES:
            time.sleep(REQUEST_DELAY)

    print(f"\n爬取完成，共获取 {len(all_loupans)} 条楼盘数据")
    if total_failures > 0:
        print(f"共有 {total_failures} 次失败，失败页面已保存到: {FAILED_PAGES_DIR}")

    # 显示代理统计
    if use_proxy and proxy_pool:
        proxy_pool.show_statistics()

    # 保存到CSV
    if all_loupans:
        save_to_csv(all_loupans, OUTPUT_FILE)

    return all_loupans, need_relogin
