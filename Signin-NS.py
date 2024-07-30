# -- coding: utf-8 --
import os
import sys
from curl_cffi import requests

# 从环境变量获取配置
NS_COOKIES = os.environ.get("NS_COOKIES", "")
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_USER_ID = os.environ.get("TG_USER_ID", "")
telegram_api_url = os.environ.get("TELEGRAM_API_URL", "https://api.telegram.org")  # 默认Telegram API

def telegram_Bot(token, TG_USER_ID, message):
    url = f'{telegram_api_url}/bot{token}/sendMessage'
    data = {
        'chat_id': TG_USER_ID,
        'text': message
    }
    r = requests.post(url, json=data)
    response_data = r.json()
    msg = response_data.get('ok', False)
    print(f"telegram推送结果：{msg}\n")

def load_send():
    global send
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
        except ImportError:
            print("加载notify.py的通知服务失败，请检查~")
    else:
        print("加载通知服务失败,缺少notify.py文件")

load_send()

if NS_COOKIES:
    url = f"https://www.nodeseek.com/api/attendance?random={int(time.time())}"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        'Cookie': NS_COOKIES
    }

    try:
        response = requests.post(url, headers=headers)
        response_data = response.json()
        print(response_data)
        message = response_data.get('message', '签到失败')
        success = response_data.get('success', 'false')

        if success == "true":
            print(message)
            if telegram_bot_token and TG_USER_ID:
                telegram_Bot(telegram_bot_token, TG_USER_ID, message)
        else:
            print(message)
            if telegram_bot_token and TG_USER_ID:
                telegram_Bot(telegram_bot_token, TG_USER_ID, message)
    except Exception as e:
        print("发生异常:", e)
        print("实际响应内容:", response.text)
else:
    print("请先设置Cookie")
