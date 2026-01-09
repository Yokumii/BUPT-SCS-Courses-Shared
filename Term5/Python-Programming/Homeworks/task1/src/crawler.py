# -*- coding: utf-8 -*-
"""
爬虫主程序
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import os
from datetime import datetime
from config import (
    BASE_URL, DISTRICTS, PAGES_PER_DISTRICT,
    HEADERS, REQUEST_DELAY, OUTPUT_FILE, CSV_COLUMNS,
    MAX_CONSECUTIVE_FAILURES, FAILED_PAGES_DIR,
    PAGE_RETRY_COUNT, RETRY_DELAY
)
from cookie_manager import load_cookies_from_file
from proxy_pool import ProxyPool, fetch_with_proxy

def build_url(district_code: str, page: int) -> str:
    """
    构建目标URL

    Args:
        district_code: 城区代码，如 'haidian'
        page: 页码，从1开始

    Returns:
        完整的URL字符串
    """
    if page == 1:
        return f"{BASE_URL}{district_code}/"
    return f"{BASE_URL}{district_code}/pg{page}/"


def parse_area(house_info: str) -> str:
    """
    从房屋信息中解析平米数

    Args:
        house_info: 房屋信息字符串，如 "2室1厅 | 89.3平米 | 南 | 精装 | 中楼层"

    Returns:
        平米数字符串，如 "89.3"
    """
    match = re.search(r'([\d.]+)平米', house_info)
    if match:
        return match.group(1)
    return ""


def parse_house_id(href: str) -> str:
    """
    从链接中解析房源编号

    Args:
        href: 房源链接，如 "/ershoufang/101123456789.html"

    Returns:
        房源编号，如 "101123456789"
    """
    match = re.search(r'/ershoufang/(\d+)\.html', href)
    if match:
        return match.group(1)
    return ""


def parse_unit_price(price_text: str) -> str:
    """
    解析单价文本

    Args:
        price_text: 单价文本，如 "单价65123元/平米" 或 "53,031元/平"

    Returns:
        单价数字，如 "65123" 或 "53031"（移除逗号）
    """
    # 移除所有逗号，然后提取数字
    clean_text = price_text.replace(',', '')
    match = re.search(r'(\d+)', clean_text)
    if match:
        return match.group(1)
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
    # 从URL中提取城区和页码
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


def parse_page(html: str, district_name: str) -> list:
    """
    解析页面，提取房源数据

    Args:
        html: 页面HTML内容
        district_name: 城区名称

    Returns:
        房源数据列表，每个元素为字典
    """
    houses = []
    soup = BeautifulSoup(html, 'html.parser')

    # 查找房源列表容器
    list_content = soup.select_one('ul.sellListContent')
    if not list_content:
        print("未找到房源列表容器")
        return houses

    # 遍历每个房源项
    for item in list_content.select('li.clear'):
        try:
            house = {}
            house['城区'] = district_name

            # 房源编号：从链接中提取
            title_link = item.select_one('.title a')
            if title_link and title_link.get('href'):
                house['房源编号'] = parse_house_id(title_link['href'])
            else:
                house['房源编号'] = ""

            # 小区名称
            position_info = item.select_one('.positionInfo a')
            house['小区名称'] = position_info.text.strip() if position_info else ""

            # 平米数：从houseInfo中解析
            house_info = item.select_one('.houseInfo')
            house['平米数（单位：平米）'] = parse_area(house_info.text) if house_info else ""

            # 总价
            total_price = item.select_one('.totalPrice span')
            house['总价(单位：万)'] = total_price.text.strip() if total_price else ""

            # 单价
            unit_price = item.select_one('.unitPrice span')
            house['单价(单位：元/平)'] = parse_unit_price(unit_price.text) if unit_price else ""

            # 只添加有效数据
            if house['房源编号']:
                houses.append(house)

        except Exception as e:
            print(f"解析房源项失败: {e}")
            continue

    return houses


def save_to_csv(data: list, filepath: str):
    """
    保存数据到CSV文件

    Args:
        data: 房源数据列表
        filepath: 输出文件路径
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(data)

    print(f"数据已保存到: {filepath}")


def crawl(cookies: dict = None, use_proxy: bool = False) -> tuple:
    """
    执行爬虫主逻辑

    Args:
        cookies: 可选的cookies字典，用于登录态
        use_proxy: 是否使用代理池

    Returns:
        (房源数据列表, 是否需要重新登录)
    """
    all_houses = []
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

    for district_name, district_code in DISTRICTS.items():
        print(f"\n开始爬取: {district_name}")

        for page in range(1, PAGES_PER_DISTRICT + 1):
            url = build_url(district_code, page)

            proxy_info = ""
            if use_proxy and proxy_pool:
                proxy_info = " [使用代理]"

            print(f"  正在爬取第 {page} 页{proxy_info}: {url}")

            html, status_code, error, retries = fetch_page_with_retry(url, cookies, proxy_pool if use_proxy else None)

            # 显示重试信息
            if retries > 0 and status_code == 200:
                print(f"    ✓ 第 {retries + 1} 次尝试成功")

            # 检查HTTP状态码
            if status_code and status_code != 200:
                reason = f"HTTP状态码错误: {status_code}"
                print(f"  ❌ {reason}")
                save_failed_page(html, url, reason, status_code)
                consecutive_failures += 1
                total_failures += 1

                # 检查是否可能是Cookie失效（常见状态码：302重定向到登录页、403禁止）
                if status_code in [302, 403, 401]:
                    print(f"状态码 {status_code} 可能表示Cookie已失效")
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
                houses = parse_page(html, district_name)

                if not houses:
                    # 获取到页面但没有解析出数据
                    reason = "未解析到房源数据（可能是Cookie失效）"
                    print(f"  ⚠️ {reason}")
                    save_failed_page(html, url, reason, status_code)
                    consecutive_failures += 1
                    total_failures += 1

                    # 如果是首页就没数据，很可能是Cookie失效
                    if page == 1:
                        print(f"首页无数据，Cookie可能已失效")
                        need_relogin = True
                else:
                    # 成功获取数据，重置连续失败计数
                    all_houses.extend(houses)
                    print(f"  ✓ 获取到 {len(houses)} 条房源数据")
                    consecutive_failures = 0

            # 检查是否需要停止爬取
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"\n连续失败 {consecutive_failures} 次，停止爬取")

                if need_relogin:
                    print(f"\n检测到可能的Cookie失效，建议重新登录获取Cookie")

                # 保存已获取的数据
                if all_houses:
                    save_to_csv(all_houses, OUTPUT_FILE)
                    print(f"\n已保存 {len(all_houses)} 条已获取的数据")

                return all_houses, need_relogin

            # 请求间隔，避免触发反爬
            time.sleep(REQUEST_DELAY)

    print(f"\n爬取完成，共获取 {len(all_houses)} 条房源数据")
    if total_failures > 0:
        print(f"共有 {total_failures} 次失败，失败页面已保存到: {FAILED_PAGES_DIR}")

    # 显示代理统计
    if use_proxy and proxy_pool:
        proxy_pool.show_statistics()

    # 保存到CSV
    if all_houses:
        save_to_csv(all_houses, OUTPUT_FILE)

    return all_houses, need_relogin

