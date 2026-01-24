import requests
import os
import time
import random
import re

def push_tg(token, chat_id, content):
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": content, "parse_mode": "HTML"}
    try:
        requests.post(url, json=data, timeout=15)
    except:
        pass

def get_like_tiebas(session):
    """自动获取你关注的贴吧列表"""
    print("正在获取关注列表...")
    url = "https://tieba.baidu.com/f/like/mylike"
    try:
        res = session.get(url, timeout=10)
        # 简单粗暴正则抓取
        names = re.findall(r'title="(.+?)"', res.text)
        # 去掉一些干扰项（可选）
        return [n for n in names if n and "贴吧" not in n]
    except Exception as e:
        print(f"获取列表失败: {e}")
        return []

def main():
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    
    if not bduss:
        print("错误：BDUSS 未配置")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"BDUSS={bduss};",
    })

    # 1. 获取 tbs
    try:
        tbs = session.get("https://tieba.baidu.com/dc/common/tbs").json().get("tbs")
    except:
        tbs = None

    if not tbs:
        push_tg(tg_token, tg_chat_id, "❌ 贴吧签到失败：BDUSS失效")
        return

    # 2. 自动获取关注的贴吧
    # 如果你在环境变量里填了 TIEBA_NAMES，就用填的；没填就全自动抓取
    manual_names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    names = manual_names if manual_names else get_like_tiebas(session)

    report = [f"<b>📬 贴吧签到报告 (2026版)</b>", f"账号：<code>{bduss[:10]}***</code>", ""]
    
    for name in names:
        time.sleep(random.uniform(1, 2)) # 稍微快点，别磨叽
        try:
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            res = session.post(url, data=data, timeout=10)
            res_json = res.json()
            
            errno = res_json.get("no")
            if errno == 0:
                report.append(f"✅ 【{name}】 签到成功")
            elif errno == 1101:
                report.append(f"🔁 【{name}】 今日已签")
            else:
                err_msg = res_json.get("error", "未知错误")
                report.append(f"❌ 【{name}】 失败: {err_msg}")
        except Exception as e:
            report.append(f"💥 【{name}】 异常: {str(e)[:20]}")

    final_report = "\n".join(report)
    print(final_report)
    push_tg(tg_token, tg_chat_id, final_report)

if __name__ == "__main__":
    main()
