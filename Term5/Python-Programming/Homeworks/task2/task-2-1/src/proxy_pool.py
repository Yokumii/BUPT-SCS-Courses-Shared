# -*- coding: utf-8 -*-
"""
IP代理池管理模块
"""

import random
import time
import requests
from typing import List, Dict, Optional
import json


class ProxyPool:
    """代理IP池管理类"""

    def __init__(self, proxy_file: str = "proxy_pool.json"):
        """
        初始化代理池

        Args:
            proxy_file: 代理配置文件路径
        """
        self.proxy_file = proxy_file
        self.proxies = []
        self.proxy_status = {}
        self.load_proxies()

    def load_proxies(self):
        """从配置文件加载代理"""
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.proxies = config.get('proxies', [])

            print(f"成功加载 {len(self.proxies)} 个代理IP")

            # 初始化代理状态
            for proxy in self.proxies:
                proxy_id = proxy.get('name', proxy.get('host'))
                self.proxy_status[proxy_id] = {
                    'success': 0,
                    'fail': 0,
                    'last_used': 0,
                    'available': True
                }
        except FileNotFoundError:
            print(f"⚠️ 代理配置文件不存在: {self.proxy_file}")
            print("请创建配置文件")
        except Exception as e:
            print(f"加载代理配置失败: {e}")

    def create_template(self, filepath: str = "proxy_pool.json"):
        """
        创建代理配置模板

        Args:
            filepath: 模板文件路径
        """
        template = {
            "proxies": [
                {
                    "name": "代理1",
                    "host": "代理IP",
                    "port": 8888,
                    "username": "",
                    "password": "",
                    "type": "http",
                    "enabled": True
                },
                {
                    "name": "代理2",
                    "host": "代理IP",
                    "port": 8888,
                    "username": "",
                    "password": "",
                    "type": "http",
                    "enabled": True
                }
            ],
            "config": {
                "strategy": "round_robin",
                "retry_times": 3,
                "timeout": 10,
                "test_url": "https://bj.lianjia.com/",
                "min_interval": 1.0
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"代理配置模板已创建: {filepath}")

    def get_proxy(self, strategy: str = "round_robin") -> Optional[Dict]:
        """
        获取一个可用代理

        Args:
            strategy: 选择策略
                - round_robin: 轮询
                - random: 随机
                - least_used: 使用最少的
                - best_performance: 成功率最高的

        Returns:
            代理配置字典，格式适用于requests
        """
        if not self.proxies:
            return None

        # 过滤可用代理
        available_proxies = [
            p for p in self.proxies
            if p.get('enabled', True)
            and self.proxy_status.get(p.get('name', p.get('host')), {}).get('available', True)
        ]

        if not available_proxies:
            print("⚠️ 没有可用代理")
            return None

        # 根据策略选择代理
        if strategy == "random":
            proxy_config = random.choice(available_proxies)
        elif strategy == "least_used":
            proxy_config = min(
                available_proxies,
                key=lambda p: self.proxy_status[p.get('name', p.get('host'))]['success']
            )
        elif strategy == "best_performance":
            proxy_config = max(
                available_proxies,
                key=lambda p: self._get_success_rate(p.get('name', p.get('host')))
            )
        else:  # round_robin
            proxy_config = available_proxies[0]

        # 构建requests格式的代理配置
        return self._build_proxy_dict(proxy_config)

    def _build_proxy_dict(self, proxy_config: Dict) -> Dict:
        """
        构建requests可用的代理字典

        Args:
            proxy_config: 代理配置

        Returns:
            {"http": "...", "https": "..."}
        """
        host = proxy_config['host']
        port = proxy_config['port']
        proxy_type = proxy_config.get('type', 'http')
        username = proxy_config.get('username', '')
        password = proxy_config.get('password', '')

        # 构建代理URL
        if username and password:
            proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{proxy_type}://{host}:{port}"

        return {
            "http": proxy_url,
            "https": proxy_url,
            "_config": proxy_config  # 保存原始配置用于统计
        }

    def _get_success_rate(self, proxy_id: str) -> float:
        """计算代理成功率"""
        status = self.proxy_status.get(proxy_id, {})
        total = status.get('success', 0) + status.get('fail', 0)
        if total == 0:
            return 0.5  # 未使用过，返回中等成功率
        return status.get('success', 0) / total

    def mark_success(self, proxy_dict: Dict):
        """
        标记代理使用成功

        Args:
            proxy_dict: get_proxy()返回的代理字典
        """
        if not proxy_dict or '_config' not in proxy_dict:
            return

        proxy_config = proxy_dict['_config']
        proxy_id = proxy_config.get('name', proxy_config.get('host'))

        if proxy_id in self.proxy_status:
            self.proxy_status[proxy_id]['success'] += 1
            self.proxy_status[proxy_id]['last_used'] = time.time()
            self.proxy_status[proxy_id]['available'] = True

    def mark_failure(self, proxy_dict: Dict):
        """
        标记代理使用失败

        Args:
            proxy_dict: get_proxy()返回的代理字典
        """
        if not proxy_dict or '_config' not in proxy_dict:
            return

        proxy_config = proxy_dict['_config']
        proxy_id = proxy_config.get('name', proxy_config.get('host'))

        if proxy_id in self.proxy_status:
            self.proxy_status[proxy_id]['fail'] += 1
            self.proxy_status[proxy_id]['last_used'] = time.time()

            # 连续失败3次，暂时标记为不可用
            if self.proxy_status[proxy_id]['fail'] >= 3:
                self.proxy_status[proxy_id]['available'] = False
                print(f"⚠️  代理 {proxy_id} 连续失败，暂时禁用")

    def test_proxy(self, proxy_dict: Dict, test_url: str = "https://bj.lianjia.com/") -> bool:
        """
        测试代理是否可用

        Args:
            proxy_dict: 代理配置
            test_url: 测试URL

        Returns:
            是否可用
        """
        try:
            # 移除_config字段用于测试
            test_proxies = {k: v for k, v in proxy_dict.items() if k != '_config'}

            response = requests.get(
                test_url,
                proxies=test_proxies,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"代理测试失败: {e}")
            return False

    def test_all_proxies(self):
        """测试所有代理"""
        print("\n开始测试所有代理...")
        print("=" * 60)

        for i, proxy_config in enumerate(self.proxies, 1):
            if not proxy_config.get('enabled', True):
                continue

            proxy_dict = self._build_proxy_dict(proxy_config)
            proxy_id = proxy_config.get('name', proxy_config.get('host'))

            print(f"\n{i}. 测试代理: {proxy_id}")
            print(f"   地址: {proxy_config['host']}:{proxy_config['port']}")

            is_available = self.test_proxy(proxy_dict)

            if is_available:
                print(f"   ✓ 可用")
                self.mark_success(proxy_dict)
            else:
                print(f"   ✗ 不可用")
                self.mark_failure(proxy_dict)

        print("\n" + "=" * 60)
        print("测试完成")
        self.show_statistics()

    def show_statistics(self):
        """显示代理统计信息"""
        print("\n代理池统计:")
        print("=" * 60)

        for proxy_id, status in self.proxy_status.items():
            total = status['success'] + status['fail']
            success_rate = self._get_success_rate(proxy_id) * 100 if total > 0 else 0

            print(f"\n{proxy_id}:")
            print(f"  成功: {status['success']} | 失败: {status['fail']}")
            print(f"  成功率: {success_rate:.1f}%")
            print(f"  状态: {'✓ 可用' if status['available'] else '✗ 不可用'}")

        print("=" * 60)


def fetch_with_proxy(url: str, proxy_pool: ProxyPool, max_retries: int = 3, **kwargs) -> Optional[requests.Response]:
    """
    使用代理池发送请求

    Args:
        url: 目标URL
        proxy_pool: 代理池实例
        max_retries: 最大重试次数
        **kwargs: 传递给requests.get的其他参数

    Returns:
        Response对象，失败返回None
    """
    for attempt in range(max_retries):
        # 获取代理
        proxy = proxy_pool.get_proxy()

        try:
            # 构建请求参数
            request_proxies = {k: v for k, v in proxy.items() if k != '_config'} if proxy else None

            response = requests.get(
                url,
                proxies=request_proxies,
                timeout=kwargs.pop('timeout', 10),
                **kwargs
            )

            # 标记成功
            if proxy:
                proxy_pool.mark_success(proxy)

            return response

        except Exception as e:
            print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")

            # 标记失败
            if proxy:
                proxy_pool.mark_failure(proxy)

            # 最后一次尝试失败
            if attempt == max_retries - 1:
                print(f"✗ 所有重试失败: {url}")
                return None

            # 等待后重试
            time.sleep(1)

    return None


if __name__ == "__main__":
    # 创建代理池实例
    pool = ProxyPool()

    # 如果配置不存在，创建模板
    if not pool.proxies:
        pool.create_template()
        print("\n请编辑 proxy_pool.json 配置文件后重新运行")
    else:
        # 测试所有代理
        pool.test_all_proxies()
