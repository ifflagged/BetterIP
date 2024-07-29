import requests
import json
import threading
import os
import re

# 从环境变量或配置文件读取 Telegram 相关配置
push_config = {
    'TG_BOT_TOKEN': os.getenv('TG_BOT_TOKEN'),
    'TG_USER_ID': os.getenv('TG_USER_ID'),
    'TG_API_HOST': os.getenv('TG_API_HOST'),
    'TG_PROXY_AUTH': os.getenv('TG_PROXY_AUTH'),
    'TG_PROXY_HOST': os.getenv('TG_PROXY_HOST'),
    'TG_PROXY_PORT': os.getenv('TG_PROXY_PORT')
}

def telegram_bot(title: str, content: str) -> None:
    """
    使用 Telegram 机器人推送消息。
    """
    if not push_config.get("TG_BOT_TOKEN") or not push_config.get("TG_USER_ID"):
        print("TG 服务的 bot_token 或者 user_id 未设置!!\n取消推送")
        return

    if push_config.get("TG_API_HOST"):
        url = f"{push_config.get('TG_API_HOST')}/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"
    else:
        url = f"https://api.telegram.org/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "chat_id": str(push_config.get("TG_USER_ID")),
        "text": f"{title}\n\n{content}",
        "disable_web_page_preview": "true",
    }

    proxies = None
    if push_config.get("TG_PROXY_HOST") and push_config.get("TG_PROXY_PORT"):
        if push_config.get("TG_PROXY_AUTH"):
            push_config["TG_PROXY_HOST"] = f"{push_config.get('TG_PROXY_AUTH')}@{push_config.get('TG_PROXY_HOST')}"
        proxy_str = f"http://{push_config.get('TG_PROXY_HOST')}:{push_config.get('TG_PROXY_PORT')}"
        proxies = {"http": proxy_str, "https": proxy_str}

    response = requests.post(url, headers=headers, data=payload, proxies=proxies).json()
    if response.get("ok"):
        print("Telegram 推送成功！")
    else:
        print(f"Telegram 推送失败！{response.get('description')}")

def merge_cookies(cookies_list):
    """
    合并多个 cookies 信息。
    """
    merged_cookies = ""
    for cookie in cookies_list:
        merged_cookies += f"{cookie}\n\n"
    return merged_cookies.strip()

def send_cookies(cookies_list):
    """
    将多个 cookies 信息合并并通过 Telegram 发送。
    """
    title = "Cookies 信息合并推送"
    content = merge_cookies(cookies_list)
    telegram_bot(title, content)

def main():
    # 示例 cookies 列表
    cookies_list = [
        "cookie1=value1; cookie2=value2",
        "cookie3=value3; cookie4=value4",
        "cookie5=value5; cookie6=value6"
    ]
    send_cookies(cookies_list)

if __name__ == "__main__":
    main()
