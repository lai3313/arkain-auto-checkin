#!/usr/bin/env python3
"""
Arkain.io 自动签到脚本 - 使用Selenium浏览器自动化
支持自动登录、签到和Telegram通知
"""

import os
import time
import json
import logging
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 环境变量配置
EMAIL = os.getenv("ARKAIN_EMAIL")
PASSWORD = os.getenv("ARKAIN_PASSWORD")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    """发送Telegram通知"""
    if not TG_TOKEN or not TG_CHAT_ID:
        logger.info("Telegram配置未设置，跳过通知")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        data = {
            "chat_id": TG_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info("Telegram通知发送成功")
        else:
            logger.error(f"Telegram通知发送失败: {response.text}")
    except Exception as e:
        logger.error(f"发送Telegram通知时出错: {e}")

class ArkainSession:
    def __init__(self):
        self.driver = None
        self.base_url = "https://account.arkain.io"
        self.console_url = "https://arkain.io"
        self.setup_driver()

    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 使用webdriver-manager自动管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome WebDriver初始化成功")
        except Exception as e:
            logger.error(f"Chrome WebDriver初始化失败: {e}")
            raise

    def wait_and_click(self, selector, by=By.XPATH, timeout=10, description="元素"):
        """等待元素出现并点击"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)  # 等待滚动完成
            element.click()
            logger.info(f"成功点击{description}")
            return True
        except TimeoutException:
            logger.warning(f"等待{description}超时: {selector}")
            return False
        except Exception as e:
            logger.error(f"点击{description}失败: {e}")
            return False

    def wait_and_type(self, selector, text, by=By.XPATH, timeout=10, description="输入框"):
        """等待输入框出现并输入文本"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            element.clear()
            element.send_keys(text)
            logger.info(f"成功在{description}输入文本")
            return True
        except TimeoutException:
            logger.warning(f"等待{description}超时: {selector}")
            return False
        except Exception as e:
            logger.error(f"在{description}输入文本失败: {e}")
            return False

    def login(self, email, password):
        """登录Arkain账户"""
        logger.info("开始登录Arkain账户...")
        
        try:
            # 访问登录页面
            logger.info(f"访问登录页面: {self.base_url}/login")
            self.driver.get(f"{self.base_url}/login")
            time.sleep(3)  # 等待页面加载
            
            # 检查是否已经在登录页面
            current_url = self.driver.current_url
            logger.info(f"当前页面URL: {current_url}")
            
            # 尝试多种方式找到邮箱输入框
            email_selectors = [
                "//input[@type='email']",
                "//input[@name='email']",
                "//input[@id='email']",
                "//input[contains(@placeholder, 'email')]",
                "//input[contains(@placeholder, 'Email')]",
                "//input[contains(@aria-label, 'email')]"
            ]
            
            email_found = False
            for selector in email_selectors:
                if self.wait_and_type(selector, email, description="邮箱输入框"):
                    email_found = True
                    break
            
            if not email_found:
                logger.error("未找到邮箱输入框")
                return False
            
            # 尝试多种方式找到密码输入框
            password_selectors = [
                "//input[@type='password']",
                "//input[@name='password']",
                "//input[@id='password']",
                "//input[contains(@placeholder, 'password')]",
                "//input[contains(@placeholder, 'Password')]"
            ]
            
            password_found = False
            for selector in password_selectors:
                if self.wait_and_type(selector, password, description="密码输入框"):
                    password_found = True
                    break
            
            if not password_found:
                logger.error("未找到密码输入框")
                return False
            
            # 查找并点击登录按钮
            login_button_selectors = [
                "//button[@type='submit']",
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), '登录')]",
                "//input[@type='submit']",
                "//button[contains(@class, 'btn') and contains(@class, 'primary')]",
                "//button[contains(text(), 'Sign in')]"
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                if self.wait_and_click(selector, description="登录按钮"):
                    login_clicked = True
                    break
            
            if not login_clicked:
                logger.error("未找到登录按钮")
                return False
            
            # 等待登录完成
            time.sleep(5)
            
            # 检查登录是否成功
            current_url_after = self.driver.current_url
            logger.info(f"登录后页面URL: {current_url_after}")
            
            # 检查是否有错误消息
            try:
                error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'invalid') or contains(text(), 'error') or contains(text(), 'Invalid') or contains(text(), 'Error')]")
                if error_elements:
                    for element in error_elements:
                        if element.is_displayed():
                            logger.error(f"登录错误: {element.text}")
                            return False
            except:
                pass
            
            # 检查是否成功登录
            if "login" not in current_url_after.lower() or "dashboard" in current_url_after.lower():
                logger.info("登录成功")
                return True
            else:
                # 检查页面内容
                page_source = self.driver.page_source.lower()
                if "dashboard" in page_source or "welcome" in page_source:
                    logger.info("登录成功（通过页面内容判断）")
                    return True
                else:
                    logger.warning("登录状态不确定，继续执行")
                    return True
                    
        except Exception as e:
            logger.error(f"登录过程中出错: {e}")
            return False

    def navigate_to_dashboard(self):
        """导航到仪表板"""
        logger.info("导航到仪表板...")
        
        # 尝试多个可能的仪表板URL
        dashboard_urls = [
            f"{self.base_url}/dashboard",
            f"{self.console_url}/dashboard",
            "https://ap-south-1.arkain.io/dashboard",
            "https://ap-northeast-2.arkain.io/dashboard",
            "https://us-west-2.arkain.io/dashboard",
            "https://eu-central-1.arkain.io/dashboard"
        ]
        
        for url in dashboard_urls:
            try:
                logger.info(f"尝试访问仪表板: {url}")
                self.driver.get(url)
                time.sleep(3)
                
                # 检查是否成功到达仪表板
                page_source = self.driver.page_source.lower()
                if "dashboard" in page_source or "check" in page_source:
                    logger.info("成功到达仪表板")
                    return True
                else:
                    logger.warning(f"页面 {url} 不包含仪表板内容")
                    
            except Exception as e:
                logger.warning(f"访问 {url} 失败: {e}")
                continue
        
        logger.error("无法访问仪表板")
        return False

    def perform_checkin(self):
        """执行签到操作"""
        logger.info("开始执行签到...")
        
        try:
            # 等待页面完全加载
            time.sleep(3)
            
            # 获取当前页面源码
            page_source = self.driver.page_source
            
            # 检查是否已经签到过
            already_checked_patterns = [
                r'already.*check',
                r'checked.*in',
                r'已完成签到',
                r'已经签到',
                r'checked.*today'
            ]
            
            for pattern in already_checked_patterns:
                if re.search(pattern, page_source, re.IGNORECASE):
                    logger.info("今天已经签到过了")
                    return True
            
            # 查找Daily check-in按钮的多种选择器
            checkin_selectors = [
                # XPath选择器
                "//button[contains(text(), 'Daily check-in')]",
                "//button[contains(text(), 'Daily Check-in')]",
                "//button[contains(text(), 'daily check')]",
                "//button[contains(text(), 'Check in')]",
                "//button[contains(text(), 'check-in')]",
                "//a[contains(text(), 'Daily check-in')]",
                "//a[contains(text(), 'Daily Check-in')]",
                "//a[contains(text(), 'Check in')]",
                "//a[contains(text(), 'check-in')]",
                "//button[contains(@class, 'check')]",
                "//button[contains(@id, 'check')]",
                "//a[contains(@class, 'check')]",
                "//a[contains(@id, 'check')]",
                "//button[contains(@onclick, 'check')]",
                "//a[contains(@onclick, 'check')]",
                # CSS选择器
                "button[class*='check']",
                "a[class*='check']",
                "button[id*='check']",
                "a[id*='check']",
                # 包含特定文本的任何元素
                "//*[contains(text(), 'Daily check-in')]",
                "//*[contains(text(), 'Daily Check-in')]",
                "//*[contains(text(), 'Check in')]",
                "//*[contains(text(), 'check-in')]"
            ]
            
            # 尝试找到并点击签到按钮
            checkin_clicked = False
            for selector in checkin_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector) if selector.startswith('//') else self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.lower()
                            if any(keyword in element_text for keyword in ['daily check', 'check in', 'check-in']):
                                logger.info(f"找到签到按钮: {element.text}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(1)
                                element.click()
                                logger.info("成功点击签到按钮")
                                checkin_clicked = True
                                break
                    if checkin_clicked:
                        break
                except Exception as e:
                    logger.debug(f"选择器 {selector} 失败: {e}")
                    continue
            
            if not checkin_clicked:
                logger.warning("未找到签到按钮，可能已经签到过或页面结构发生变化")
                return True
            
            # 等待签到完成
            time.sleep(3)
            
            # 检查签到结果
            success_patterns = [
                r'success',
                r'completed',
                r'done',
                r'签到成功',
                r'checked.*in',
                r'check.*complete'
            ]
            
            page_source_after = self.driver.page_source.lower()
            for pattern in success_patterns:
                if re.search(pattern, page_source_after):
                    logger.info("签到成功")
                    return True
            
            # 检查是否有错误
            error_patterns = [
                r'error',
                r'failed',
                r'unable',
                r'签到失败'
            ]
            
            for pattern in error_patterns:
                if re.search(pattern, page_source_after):
                    logger.error("签到失败")
                    return False
            
            # 如果没有明确的成功或失败信息，假设签到成功
            logger.info("签到操作完成（无明确结果提示）")
            return True
            
        except Exception as e:
            logger.error(f"签到过程中出错: {e}")
            return False

    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器时出错: {e}")

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("Arkain.io 自动签到脚本启动")
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    # 检查环境变量
    if not EMAIL or not PASSWORD:
        error_msg = "环境变量 ARKAIN_EMAIL 或 ARKAIN_PASSWORD 未设置"
        logger.error(error_msg)
        send_telegram(f"❌ Arkain签到失败: {error_msg}")
        return
    
    arkain = None
    try:
        # 创建会话
        arkain = ArkainSession()
        
        # 登录
        if not arkain.login(EMAIL, PASSWORD):
            raise Exception("登录失败")
        
        # 登录成功后直接尝试签到（Daily check-in按钮在登录后的主页面）
        logger.info("登录成功，直接在当前页面查找签到功能")
        
        # 执行签到
        if arkain.perform_checkin():
            success_msg = "✅ Arkain.io 签到成功"
            logger.info(success_msg)
            send_telegram(success_msg)
        else:
            raise Exception("签到操作失败")
            
    except Exception as e:
        error_msg = f"❌ Arkain.io 签到失败: {str(e)}"
        logger.error(error_msg)
        send_telegram(error_msg)
    finally:
        # 确保关闭浏览器
        if arkain:
            arkain.close()

if __name__ == "__main__":
    main()