from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import time
import requests

# 环境变量
EMAIL = os.getenv("ARKAIN_EMAIL")
PASSWORD = os.getenv("ARKAIN_PASSWORD")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if TG_TOKEN and TG_CHAT_ID:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg})

# Selenium 配置
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    # 登录 Arkain
    driver.get("https://ap-south-1.arkain.io/login")
    time.sleep(3)
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
    time.sleep(5)

    # 跳转仪表板并签到
    driver.get("https://ap-south-1.arkain.io/dashboard")
    time.sleep(5)
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Daily check-in')]")
    button.click()
    send_telegram("✅ Arkain 签到成功")
    print("✅ 签到成功")

except Exception as e:
    send_telegram(f"❌ Arkain 签到失败: {e}")
    print("❌ 签到失败:", e)

finally:
    driver.quit()
