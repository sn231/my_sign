import requests
import os
import time
import random

def push_tg(token, chat_id, content):
    """把结果推送到 Telegram"""
    if not token or not chat_id:
        print("未配置 TG 通知，跳过。")
        return
    print("正在发送 TG 通知...")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": content,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=data, timeout=15).json()
        if res.get("ok"):
            print("TG 通知发送成功！")
        else:
            print(f"TG 通知失败：{res.get('description')}")
    except Exception as e:
        print(f"TG 通知异常：{e}")

def main():
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    
    if not bduss or not names:
        print("错误：Secrets 配置缺失")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"BDUSS={bduss};",
        "Referer": "https://tieba.baidu.com/"
    })

    # 1. 拿 tbs
    try:
        tbs_res = session.get("https://tieba.baidu.com/dc/common/tbs", timeout=10).json()
        tbs = tbs_res.get("tbs")
    except:
        tbs = None

    if not tbs:
        msg = "<b>❌ 贴吧签到失败</b>\n原因：无法获取 tbs，BDUSS 可能失效。"
        push_tg(tg_token, tg_chat_id, msg)
        return

    # 2. 签到
    report = [f"<b>📬 贴吧签到报告</b>", f"账号：<code>{bduss[:10]}***</code>", ""]
    
    for name in names:
        time.sleep(random.uniform(2, 4))
        try:
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            res = session.post(url, data=data, timeout=10, allow_redirects=False)
            res_json = res.json()
            if res_json.get("no") in [0, 1101]:
                report.append(f"✅ 【{name}】 成功")
            else:
                report.append(f"❌ 【{name}】 失败({res_json.get('error')})")
        except:
            report.append(f"💥 【{name}】 崩溃")

    # 3. 发送通知
    final_report = "\n".join(report)
    print(final_report)
    push_tg(tg_token, tg_chat_id, final_report)

if __name__ == "__main__":
    main()
