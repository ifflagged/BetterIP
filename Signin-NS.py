# -- coding: utf-8 --
import os
import sys
from curl_cffi import requests
import datetime

# 从环境变量中获取Telegram相关信息
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_USER_ID = os.environ.get("TG_USER_ID", "")
telegram_api_url = os.environ.get("TELEGRAM_API_URL", "https://api.telegram.org")

def telegram_Bot(token, TG_USER_ID, message):
    url = f'{telegram_api_url}/bot{token}/sendMessage'
    data = {
        'chat_id': TG_USER_ID,
        'text': message
    }
    r = requests.post(url, json=data)
    response_data = r.json()
    msg = response_data['ok']
    print(f"Telegram推送结果：{msg}\n")

def load_send():
    global send
    hadsend = False
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
            hadsend = True
        except:
            print("加载notify.py的通知服务失败，请检查~")
    else:
        print("加载通知服务失败,缺少notify.py文件")

load_send()

# 从环境变量获取Cookie
COOKIE_ENV = os.environ.get("NS_COOKIE")
if COOKIE_ENV:
    url = f"https://www.nodeseek.com/api/attendance?random={datetime.datetime.now().timestamp()}"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        'sec-ch-ua': "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"",
        'sec-ch-ua-mobile': "?0",
        'sec-ch-ua-platform': "\"Windows\"",
        'origin': "https://www.nodeseek.com",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://www.nodeseek.com/board",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        'Cookie': COOKIE_ENV
    }

    try:
        response = requests.post(url, headers=headers)
        response_data = response.json()
        print(response_data)
        message = response_data.get('message')
        success = response_data.get('success')

        if telegram_bot_token and TG_USER_ID:
            telegram_Bot(telegram_bot_token, TG_USER_ID, message)

        if success == "true":
            print("签到成功：", message)
        else:
            print("签到失败：", message)
    except Exception as e:
        print("发生异常:", e)
else:
    print("请先设置Cookie")
