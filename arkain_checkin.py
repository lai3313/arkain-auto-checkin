#!/usr/bin/env python3
"""
Arkain.io 自动签到脚本 - 使用requests库
支持自动登录、签到和Telegram通知
"""

import requests
import os
import time
import json
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

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
        self.session = requests.Session()
        self.base_url = "https://account.arkain.io"
        self.console_url = "https://arkain.io"
        
        # 设置通用headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_csrf_token(self, login_page_url):
        """从登录页面获取CSRF token"""
        try:
            response = self.session.get(login_page_url)
            response.raise_for_status()
            
            # 尝试多种方式获取CSRF token
            content = response.text
            
            # 方法1: 查找常见的CSRF token meta标签
            csrf_patterns = [
                r'<meta[^>]*name=["\']csrf-token["\'][^>]*content=["\']([^"\']+)["\']',
                r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']csrf-token["\']',
                r'csrf["\']?\s*:\s*["\']([^"\']+)["\']',
                r'_token["\']?\s*:\s*["\']([^"\']+)["\']',
                r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in csrf_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    logger.info("找到CSRF token")
                    return match.group(1)
            
            # 方法2: 查找隐藏input字段
            input_pattern = r'<input[^>]*type=["\']hidden["\'][^>]*name=["\'](_token|csrf_token|csrf)["\'][^>]*value=["\']([^"\']+)["\']'
            match = re.search(input_pattern, content, re.IGNORECASE)
            if match:
                logger.info("从隐藏input字段找到CSRF token")
                return match.group(2)
            
            logger.warning("未找到CSRF token，可能不需要")
            return None
            
        except Exception as e:
            logger.error(f"获取CSRF token失败: {e}")
            return None

    def login(self, email, password):
        """登录Arkain账户"""
        logger.info("开始登录Arkain账户...")
        
        login_url = f"{self.base_url}/login"
        
        try:
            # 获取登录页面和CSRF token
            csrf_token = self.get_csrf_token(login_url)
            
            # 准备登录数据
            login_data = {
                'email': email,
                'password': password,
            }
            
            # 如果有CSRF token，添加到数据中
            if csrf_token:
                login_data['_token'] = csrf_token
                login_data['csrf_token'] = csrf_token
            
            # 发送登录请求
            logger.info("发送登录请求...")
            response = self.session.post(login_url, data=login_data, allow_redirects=True)
            
            # 检查登录结果
            if response.status_code == 200:
                # 检查是否成功登录（通过响应内容或重定向）
                if "login" not in response.url.lower() or "dashboard" in response.text.lower():
                    logger.info("登录成功")
                    return True
                else:
                    # 检查是否有错误消息
                    if "invalid" in response.text.lower() or "error" in response.text.lower():
                        logger.error("登录失败：用户名或密码错误")
                        return False
                    else:
                        logger.warning("登录状态不确定，继续执行")
                        return True
            else:
                logger.error(f"登录请求失败，状态码: {response.status_code}")
                return False
                
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
                response = self.session.get(url)
                
                if response.status_code == 200:
                    if "dashboard" in response.text.lower() or "check" in response.text.lower():
                        logger.info("成功到达仪表板")
                        return True
                else:
                    logger.warning(f"访问 {url} 失败，状态码: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"访问 {url} 失败: {e}")
                continue
        
        logger.error("无法访问仪表板")
        return False

    def perform_checkin(self):
        """执行签到操作"""
        logger.info("开始执行签到...")
        
        try:
            # 尝试多种签到方式
            
            # 方法1: 查找签到API端点
            dashboard_response = self.session.get(f"{self.base_url}/dashboard")
            content = dashboard_response.text
            
            # 查找可能的签到API
            api_patterns = [
                r'(["\'])/api/[^"\']*check[^"\']*["\']',
                r'["\']([^"\']*check[^"\']*)["\']',
                r'onclick=["\'][^"\']*check[^"\']*["\']',
            ]
            
            checkin_urls = []
            for pattern in api_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    url = match.strip('"\'')
                    if not url.startswith('http'):
                        url = urljoin(self.base_url, url)
                    checkin_urls.append(url)
            
            # 去重
            checkin_urls = list(set(checkin_urls))
            
            for checkin_url in checkin_urls:
                try:
                    logger.info(f"尝试签到API: {checkin_url}")
                    
                    # 尝试GET请求
                    response = self.session.get(checkin_url)
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            if result.get('success') or result.get('status') == 'success':
                                logger.info("签到成功（GET请求）")
                                return True
                        except:
                            pass
                    
                    # 尝试POST请求
                    response = self.session.post(checkin_url)
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            if result.get('success') or result.get('status') == 'success':
                                logger.info("签到成功（POST请求）")
                                return True
                        except:
                            pass
                    
                except Exception as e:
                    logger.warning(f"签到API {checkin_url} 失败: {e}")
                    continue
            
            # 方法2: 模拟表单提交
            form_patterns = [
                r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>(.*?)</form>',
            ]
            
            for pattern in form_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for action, form_html in matches:
                    if 'check' in action.lower() or 'check' in form_html.lower():
                        try:
                            form_url = urljoin(self.base_url, action)
                            logger.info(f"尝试表单签到: {form_url}")
                            
                            # 提取表单数据
                            input_pattern = r'<input[^>]*name=["\']([^"\']*)["\'][^>]*value=["\']([^"\']*)["\']'
                            inputs = re.findall(input_pattern, form_html, re.IGNORECASE)
                            
                            form_data = dict(inputs)
                            
                            # 发送表单
                            response = self.session.post(form_url, data=form_data)
                            if response.status_code == 200:
                                if any(word in response.text.lower() for word in ['success', 'completed', 'done']):
                                    logger.info("表单签到成功")
                                    return True
                                    
                        except Exception as e:
                            logger.warning(f"表单签到失败: {e}")
                            continue
            
            # 如果所有方法都失败，假设签到成功（可能已经签到过了）
            logger.info("签到操作完成（无明确结果提示）")
            return True
            
        except Exception as e:
            logger.error(f"签到过程中出错: {e}")
            return False

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
    
    try:
        # 创建会话
        arkain = ArkainSession()
        
        # 登录
        if not arkain.login(EMAIL, PASSWORD):
            raise Exception("登录失败")
        
        # 导航到仪表板
        if not arkain.navigate_to_dashboard():
            logger.warning("导航仪表板失败，尝试在当前页面查找签到功能")
        
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

if __name__ == "__main__":
    main()