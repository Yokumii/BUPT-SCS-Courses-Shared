# -*- coding: utf-8 -*-
"""
Cookie管理模块
"""

import json
import os


def load_cookies_from_file(filepath: str = "cookies.json") -> dict:
    """
    从JSON文件加载cookies

    Args:
        filepath: cookies文件路径

    Returns:
        cookies字典
    """
    if not os.path.exists(filepath):
        print(f"Cookie文件不存在: {filepath}")
        return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        print(f"成功加载Cookie: {filepath}")
        return cookies
    except Exception as e:
        print(f"加载Cookie失败: {e}")
        return {}


def save_cookies_to_file(cookies: dict, filepath: str = "cookies.json"):
    """
    保存cookies到JSON文件

    Args:
        cookies: cookies字典
        filepath: 保存路径
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"Cookie已保存到: {filepath}")
    except Exception as e:
        print(f"保存Cookie失败: {e}")
