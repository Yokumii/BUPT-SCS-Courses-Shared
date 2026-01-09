# -*- coding: utf-8 -*-
"""
基于Selenium的链家自动登录模块
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import time


class AutoLogin:
    """链家自动登录类"""

    def __init__(self, headless=False):
        """
        初始化Selenium WebDriver

        Args:
            headless: 是否使用无头模式
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')

        # 去除自动化特征
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })

    def login_manual(self, wait_time=120):
        """
        自动打开登录页，等待用户手动完成登录

        Args:
            wait_time: 等待用户登录的最长时间（秒）

        Returns:
            cookies: 登录成功后的Cookie字典
        """
        print("=" * 60)
        print("链家自动登录")
        print("=" * 60)

        # 打开链家首页
        self.driver.get("https://bj.lianjia.com/")
        print("\n已打开链家首页")

        # 等待页面加载
        time.sleep(2)

        # 查找并点击登录按钮
        try:
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "登录"))
            )
            login_btn.click()
            print("✓ 已点击登录按钮")
        except:
            print("⚠ 未找到登录按钮，请手动点击")

        time.sleep(2)

        print("\n" + "=" * 60)
        print("请在浏览器中完成登录操作")
        print("=" * 60)

        # 等待用户登录成功（检测关键Cookie）
        start_time = time.time()
        logged_in = False

        print("\n正在等待登录完成...")

        while time.time() - start_time < wait_time:
            # 获取当前Cookie并检查关键认证Cookie是否存在
            current_cookies = self.driver.get_cookies()
            cookie_dict = {c['name']: c['value'] for c in current_cookies}

            # 检测关键Cookie（至少要有lianjia_token或login_ucid）
            has_token = 'lianjia_token' in cookie_dict and len(cookie_dict['lianjia_token']) > 10
            has_ucid = 'login_ucid' in cookie_dict and len(cookie_dict['login_ucid']) > 10

            if has_token or has_ucid:
                # 额外等待2秒确保所有Cookie都已设置
                time.sleep(2)
                logged_in = True
                break

            # 每5秒输出一次等待提示
            elapsed = int(time.time() - start_time)
            if elapsed > 0 and elapsed % 5 == 0:
                remaining = wait_time - elapsed
                print(f"等待中... (剩余 {remaining} 秒)")

            time.sleep(1)

        if logged_in:
            print("\n✓ 登录成功！")
            cookies = self.get_cookies()
            if cookies:
                # 自动保存Cookie到文件
                self.save_cookies(cookies)
            return cookies
        else:
            print(f"\n⚠ 登录超时（{wait_time}秒），请重试")
            return None

    def get_cookies(self):
        """
        获取当前会话的所有Cookie，并验证关键Cookie

        Returns:
            cookies: Cookie字典
        """
        selenium_cookies = self.driver.get_cookies()

        # 转换为requests可用的格式
        cookies = {}
        for cookie in selenium_cookies:
            cookies[cookie['name']] = cookie['value']

        print(f"\n成功获取 {len(cookies)} 个Cookie")

        # 显示并验证关键Cookie
        key_cookies = ["lianjia_token", "lianjia_token_secure", "login_ucid"]
        valid_count = 0

        print("\n关键认证Cookie:")
        for key in key_cookies:
            if key in cookies:
                value = cookies[key]
                display_value = value[:20] + "..." if len(value) > 20 else value
                print(f"  ✓ {key}: {display_value}")
                valid_count += 1
            else:
                print(f"  ⚠ {key}: 未找到")

        # 如果关键Cookie不足
        if valid_count == 0:
            print("\n⚠️  警告：未找到任何关键认证Cookie！")
            return None

        return cookies

    def save_cookies(self, cookies, filepath="cookies.json"):
        """
        保存Cookie到文件

        Args:
            cookies: Cookie字典
            filepath: 保存路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Cookie已保存到: {filepath}")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def main():
    """测试一下登录"""

    auto_login = LianjiaAutoLogin(headless=False)

    try:
        # 半自动登录，等待用户手动完成
        cookies = auto_login.login_manual(
            phone=phone if phone else None,
            wait_time=120  # 等待2分钟
        )

        if cookies:
            # 保存Cookie
            auto_login.save_cookies(cookies)
        else:
            print("\n✗ 登录失败或Cookie无效")

    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 询问是否关闭浏览器
        print("\n是否关闭浏览器？(y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                auto_login.close()
                print("浏览器已关闭")
            else:
                print("浏览器保持打开，按任意键退出程序...")
                input()
                auto_login.close()
        except:
            auto_login.close()


if __name__ == "__main__":
    main()
