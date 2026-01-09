#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
链家二手房爬虫 - 主程序入口
"""

import os
import sys
from cookie_manager import load_cookies_from_file
from auto_login import AutoLogin
from crawler import crawl


def get_cookies_via_login() -> dict:
    """
    通过自动登录获取Cookie

    Returns:
        cookies字典，如果获取失败返回空字典
    """
    print("\n启动自动登录流程...")
    print("=" * 60)

    try:
        auto_login = AutoLogin()
        cookies = auto_login.login_manual(wait_time=120)

        if cookies:
            print("\n✓ 登录成功！Cookie已保存")
            return cookies
        else:
            print("\n✗ 登录失败")
            return {}

    except Exception as e:
        print(f"\n✗ 登录过程出错: {e}")
        return {}


def check_and_get_cookies() -> dict:
    """
    检查Cookie文件是否存在，如不存在则自动启动登录流程

    Returns:
        cookies字典，如果获取失败返回空字典
    """
    cookie_file = "cookies.json"

    # 尝试加载现有Cookie
    cookies = load_cookies_from_file(cookie_file)

    if cookies:
        print("已加载现有Cookie")
        return cookies

    # Cookie不存在，自动启动登录流程
    print("\n⚠️ 未检测到Cookie文件")
    return get_cookies_via_login()


def main():
    """主程序入口"""
    print("=" * 60)
    print("链家二手房爬虫")
    print("=" * 60)

    cookies = check_and_get_cookies()

    if not cookies:
        print("\n无法获取Cookie，程序退出")
        return

    print("\n是否使用代理池? (y/n): ", end="")
    use_proxy_choice = input().strip().lower()
    use_proxy = (use_proxy_choice == 'y')

    print("\n开始爬取...")

    # 执行爬虫
    houses, need_relogin = crawl(cookies, use_proxy=use_proxy)

    # 如果检测到Cookie失效，提示重新登录
    if need_relogin:
        print("\n" + "=" * 60)
        print("检测到Cookie可能已失效")
        print("是否立即重新登录? (y/n): ", end="")
        relogin_choice = input().strip().lower()

        if relogin_choice == 'y':
            # 删除旧的Cookie文件
            cookie_file = "cookies.json"
            if os.path.exists(cookie_file):
                os.remove(cookie_file)
                print("已删除旧Cookie文件")

            # 重新登录
            new_cookies = get_cookies_via_login()

            if new_cookies:
                print("\n是否使用新Cookie继续爬取? (y/n): ", end="")
                continue_choice = input().strip().lower()

                if continue_choice == 'y':
                    print("\n继续爬取...")
                    crawl(new_cookies, use_proxy=use_proxy)


if __name__ == "__main__":
    main()
