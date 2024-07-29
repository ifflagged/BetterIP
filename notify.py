#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import json
import os
import re
import threading
import requests

# 原先的 print 函数和主线程的锁
_print = print
mutex = threading.Lock()

# 定义新的 print 函数
def print(text, *args, **kw):
    """
    使输出有序进行，不出现多线程同一时间输出导致错乱的问题。
    """
    with mutex:
        _print(text, *args, **kw)

# Telegram 配置
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
        print("tg 服务的 bot_token 或者 user_id 未设置!!\n取消推送")
        return
    print("tg 服务启动")

    if push_config.get("TG_API_HOST"):
        url = f"{push_config.get('TG_API_HOST')}/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"
    else:
        url = (
            f"https://api.telegram.org/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"
        )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "chat_id": str(push_config.get("TG_USER_ID")),
        "text": f"{title}\n\n{content}",
        "disable_web_page_preview": "true",
    }
    proxies = None
    if push_config.get("TG_PROXY_HOST") and push_config.get("TG_PROXY_PORT"):
        if push_config.get("TG_PROXY_AUTH") is not None and "@" not in push_config.get(
            "TG_PROXY_HOST"
        ):
            push_config["TG_PROXY_HOST"] = (
                push_config.get("TG_PROXY_AUTH")
                + "@"
                + push_config.get("TG_PROXY_HOST")
            )
        proxyStr = "http://{}:{}".format(
            push_config.get("TG_PROXY_HOST"), push_config.get("TG_PROXY_PORT")
        )
        proxies = {"http": proxyStr, "https": proxyStr}
    response = requests.post(
        url=url, headers=headers, data=payload, proxies=proxies
    ).json()

    if response.get("ok"):
        print("tg 推送成功！")
    else:
        print(f"tg 推送失败！{response.get('description')}")

def merge_cookies(cookies_list):
    """
    合并多个 cookies 签到结果。
    """
    merged_results = []
    for index, cookies in enumerate(cookies_list, start=1):
        merged_results.append(f"用户 {index} 的签到结果：\n{cookies}")
    return "\n\n".join(merged_results)

def send_cookies(cookies_list):
    """
    合并多个 cookies 签到结果并通过 Telegram 发送。
    """
    title = "多个用户的 Cookies 签到结果"
    content = merge_cookies(cookies_list)
    telegram_bot(title, content)

def main():
    # 示例 cookies 列表
    cookies_list = [
        "用户1: cookie1=value1; cookie2=value2",
        "用户2: cookie3=value3; cookie4=value4",
        "用户3: cookie5=value5; cookie6=value6"
    ]
    send_cookies(cookies_list)

if __name__ == "__main__":
    main()
