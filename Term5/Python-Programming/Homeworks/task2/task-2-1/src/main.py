# -*- coding: utf-8 -*-
"""
主程序入口
"""

import os
from cookie_manager import load_cookies_from_file, save_cookies_to_file
from auto_login import AutoLogin
from crawler import crawl
from data_processor import process_data, analyze_statistics


def check_and_get_cookies() -> dict:
    """
    检查并获取Cookie

    Returns:
        Cookie字典，如果获取失败则返回None
    """
    print("=" * 60)
    print("链家新房爬虫 - Cookie管理")
    print("=" * 60)

    # 尝试从文件加载Cookie
    cookies = load_cookies_from_file()

    if cookies:
        print("\n✓ 成功从文件加载Cookie")
        print(f"  包含 {len(cookies)} 个Cookie项")
        return cookies

    print("\n⚠️ 本地没有Cookie文件，需要登录获取")
    return get_cookies_via_login()


def get_cookies_via_login() -> dict:
    """
    通过自动登录获取Cookie

    Returns:
        Cookie字典，如果失败则返回None
    """
    print("\n启动自动登录流程...")
    print("提示: 程序会打开浏览器，请手动完成登录操作")
    print("      （包括输入手机号、验证码、人机验证等）")

    try:
        login = AutoLogin()
        cookies = login.login_manual(wait_time=120)

        if cookies:
            print("\n✓ 登录成功，Cookie已保存")
            return cookies
        else:
            print("\n❌ 登录超时或失败")
            return None

    except Exception as e:
        print(f"\n❌ 登录过程出错: {e}")
        return None


def main():
    """主函数"""
    # 1. Cookie检查与获取
    cookies = check_and_get_cookies()
    if not cookies:
        print("\n无法获取Cookie，程序退出")
        return

    # 2. 询问是否使用代理
    print("\n" + "=" * 60)
    use_proxy_input = input("是否使用代理池? (y/n，默认n): ").strip().lower()
    use_proxy = use_proxy_input == 'y'

    # 3. 执行爬虫
    print("\n" + "=" * 60)
    print("开始爬取数据")
    print("=" * 60)

    loupans, need_relogin = crawl(cookies, use_proxy=use_proxy)

    # 4. Cookie失效处理
    if need_relogin:
        print("\n" + "=" * 60)
        print("检测到Cookie可能已失效")
        print("=" * 60)
        relogin = input("\n是否重新登录? (y/n): ").strip().lower()

        if relogin == 'y':
            # 删除旧Cookie文件
            if os.path.exists("cookies.json"):
                os.remove("cookies.json")

            # 重新登录
            new_cookies = get_cookies_via_login()

            # 使用新Cookie继续爬取
            if new_cookies:
                print("\n使用新Cookie继续爬取...")
                loupans, _ = crawl(new_cookies, use_proxy=use_proxy)

    # 5. 数据预处理和统计分析
    if loupans and len(loupans) > 0:
        print("\n" + "=" * 60)
        auto_process = input("是否立即进行数据预处理和统计分析? (y/n，默认y): ").strip().lower()

        if auto_process != 'n':
            from config import OUTPUT_FILE, PROCESSED_FILE
            df = process_data(OUTPUT_FILE, PROCESSED_FILE)
            analyze_statistics(df)
    else:
        print("\n⚠️ 没有爬取到数据，跳过数据处理")

    print("\n" + "=" * 60)
    print("程序执行完毕")
    print("=" * 60)


if __name__ == "__main__":
    main()
