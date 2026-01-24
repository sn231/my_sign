import requests
import os
import time
import random

def push_tg(token, chat_id, content):
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": content, "parse_mode": "HTML"}
    try: requests.post(url, json=data, timeout=15)
    except: pass

def get_like_tiebas(session):
    """【稳健版】通过 JSON 接口获取关注列表，彻底解决乱码"""
    print("正在获取关注列表...")
    url = "https://tieba.baidu.com/mo/q/newmoindex"
    try:
        res = session.get(url, timeout=10).json()
        if res.get("no") == 0:
            # 直接从 JSON 数据里提取贴吧名
            # list 是关注的贴吧数组
            tieba_list = res.get("data", {}).get("like_forum", [])
            names = [item.get("forum_name") for item in tieba_list if item.get("forum_name")]
            print(f"成功获取到 {len(names)} 个贴吧")
            return names
        else:
            print(f"接口返回错误: {res.get('error')}")
            return []
    except Exception as e:
        print(f"获取列表异常: {e}")
        return []

def main():
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    
    if not bduss:
        print("错误：BDUSS 配置缺失")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"BDUSS={bduss};",
        "Referer": "https://tieba.baidu.com/"
    })

    # 1. 获取 tbs
    try:
        tbs_res = session.get("https://tieba.baidu.com/dc/common/tbs", timeout=10).json()
        tbs = tbs_res.get("tbs")
    except:
        tbs = None

    if not tbs:
        print("TBS 获取失败")
        return

    # 2. 贴吧列表逻辑：依然保留你的覆盖功能
    manual_names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    if manual_names:
        names = manual_names
        print(f"使用手动配置的贴吧列表")
    else:
        names = get_like_tiebas(session)

    if not names:
        print("未获取到贴吧列表")
        return

    report = [f"<b>📬 贴吧签到报告</b>", f"账号：<code>{bduss[:10]}***</code>", ""]
    
    # 3. 签到（完全沿用你最早能跑通的逻辑）
    for name in names:
        time.sleep(random.uniform(2, 4))
        try:
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            # 这里保持你原来的 allow_redirects=False
