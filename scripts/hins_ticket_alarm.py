#!/usr/bin/env python3
"""张敬轩澳门演唱会开售闹钟：按服务器时间倒计时，到点在你自己的浏览器里打开购票页。

不做任何自动登录/下单，只负责提醒 + 准时打开页面。
用法: python3 scripts/hins_ticket_alarm.py [--at "2026-10-28 15:00:00"] [--lead 20]
"""
import argparse
import subprocess
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

SHOW_URL = "https://cn.cotaiticketing.com/shows/hinscheung2026.html"
LOGIN_URL = "https://box.cotaiticketing.com/zh-hans/account/preferences/?next=https%3A%2F%2Fbooking.cotaiticketing.com%2F"
MACAU = timezone(timedelta(hours=8))


def server_offset():
    """服务器时间 - 本机时间（秒），取 HTTP Date 头。"""
    t0 = time.time()
    req = urllib.request.Request(SHOW_URL, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        date = r.headers["Date"]
    t1 = time.time()
    return parsedate_to_datetime(date).timestamp() - (t0 + t1) / 2


def notify(msg):
    subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "抢票提醒" sound name "Glass"'])
    subprocess.run(["say", "-v", "Tingting", msg])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--at", default="2026-10-28 15:00:00", help="开售时间（澳门时间）")
    p.add_argument("--lead", type=int, default=20, help="提前多少秒打开购票页")
    args = p.parse_args()

    target = datetime.strptime(args.at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=MACAU).timestamp()
    try:
        off = server_offset()
        print(f"服务器时间偏差: {off:+.2f}s（Date 头精度 1s）")
    except Exception as e:
        off = 0.0
        print(f"取服务器时间失败，用本机时间: {e}")

    milestones = {600: "还有10分钟，先登录账号、确认信用卡", 120: "还有2分钟", 60: "还有1分钟"}
    opened = False
    while True:
        remain = target - (time.time() + off)
        for sec, msg in list(milestones.items()):
            if remain <= sec:
                notify(msg)
                del milestones[sec]
        if not opened and remain <= args.lead:
            subprocess.run(["open", LOGIN_URL])
            notify("购票页已打开，开始抢！")
            opened = True
        if remain <= 0:
            print("已到开售时间。进了排队就别刷新。")
            break
        print(f"\r距开售 {int(remain // 60):02d}:{remain % 60:05.2f}", end="", flush=True)
        time.sleep(0.2 if remain < 30 else 1)


if __name__ == "__main__":
    main()
