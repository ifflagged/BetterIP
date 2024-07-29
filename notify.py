#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import requests
import threading
import os
import re

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

# Telegram 推送配置
push_config = {
    'TG_BOT_TOKEN': '',  # tg 机器人的 TG_BOT_TOKEN，例：1407203283:AAG9rt-6RDaaX0HBLZQq0laNOh898iFYaRQ
    'TG_USER_ID': '',    # tg 机器人的 TG_USER_ID，例：1434078534
    'TG_API_HOST': '',   # tg 代理 api
    'TG_PROXY_AUTH': '', # tg 代理认证参数
    'TG_PROXY_HOST': '', # tg 机器人的 TG_PROXY_HOST
    'TG_PROXY_PORT': ''  # tg 机器人的 TG_PROXY_PORT
}

# 首先读取 面板变量 或者 github action 运行变量
for k in push_config:
    if os.getenv(k):
        v = os.getenv(k)
        push_config[k] = v

def telegram_bot(title: str, content: str) -> None:
    """
    使用 telegram 机器人 推送消息。
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
        url=url, headers=headers, params=payload, proxies=proxies
    ).json()

    if response["ok"]:
        print("tg 推送成功！")
    else:
        print("tg 推送失败！")

def send(title: str, contents: list, **kwargs):
    if kwargs:
        global push_config
        push_config.update(kwargs)

    if not contents:
        print(f"{title} 推送内容为空！")
        return

    # 根据标题跳过一些消息推送，环境变量：SKIP_PUSH_TITLE 用回车分隔
    skipTitle = os.getenv("SKIP_PUSH_TITLE")
    if skipTitle:
        if title in re.split("\n", skipTitle):
            print(f"{title} 在SKIP_PUSH_TITLE环境变量内，跳过推送！")
            return

    # 合并内容
    combined_content = "\n\n".join(contents)

    notify_function = [telegram_bot]  # 只使用 telegram_bot 作为推送函数
    ts = [
        threading.Thread(target=mode, args=(title, combined_content), name=mode.__name__)
        for mode in notify_function
    ]
    [t.start() for t in ts]
    [t.join() for t in ts]

def main():
    # 传递多个内容进行合并
    send("title", ["content part 1", "content part 2", "content part 3"])

if __name__ == "__main__":
    main()
