# -- coding: utf-8 --
import os
import sys
import requests  # 使用requests库替代curl_cffi

NS_RANDOM = os.environ.get("NS_RANDOM", "false")
NS_COOKIES = os.environ.get("NS_COOKIES", "").split(',')
pushplus_token = os.environ.get("PUSHPLUS_TOKEN")
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
chat_id = os.environ.get("CHAT_ID", "")
telegram_api_url = os.environ.get("TELEGRAM_API_URL", "https://api.telegram.org")  # 代理API，可以使用自己的反代

def telegram_Bot(token, chat_id, message):
    url = f'{telegram_api_url}/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, json=data)
        response_data = response.json()
        msg = response_data.get('ok', False)
        print(f"telegram推送结果：{msg}\n")
    except Exception as e:
        print(f"Telegram 推送失败: {e}")

def pushplus_ts(token, rw, msg):
    url = 'https://www.pushplus.plus/send/'
    data = {
        "token": token,
        "title": rw,
        "content": msg
    }
    try:
        response = requests.post(url, json=data)
        msg = response.json().get('msg', None)
        print(f'pushplus推送结果：{msg}\n')
    except Exception as e:
        print(f"PushPlus 推送失败: {e}")

def load_send():
    global send
    global hadsend
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
            hadsend = True
        except ImportError:
            print("加载notify.py的通知服务失败，请检查~")
            hadsend = False
    else:
        print("加载通知服务失败,缺少notify.py文件")
        hadsend = False

load_send()

def process_cookie(cookie):
    url = f"https://www.nodeseek.com/api/attendance?random={NS_RANDOM}"
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
        'Cookie': cookie
    }

    try:
        response = requests.post(url, headers=headers)
        response_data = response.json()
        print(response_data)
        message = response_data.get('message', 'No message')
        success = response_data.get('success', 'false')
        if hadsend:
            send("nodeseek签到", [message])
        if success == "true":
            print(message)
            if telegram_bot_token and chat_id:
                telegram_Bot(telegram_bot_token, chat_id, message)
        else:
            print(message)
            if telegram_bot_token and chat_id:
                telegram_Bot(telegram_bot_token, chat_id, message)
            if pushplus_token:
                pushplus_ts(pushplus_token, "nodeseek签到", message)
    except Exception as e:
        print(f"发生异常: {e}")

if NS_COOKIES:
    for cookie in NS_COOKIES:
        cookie = cookie.strip()
        if cookie:
            process_cookie(cookie)
else:
    print("请先设置NS_COOKIES")
