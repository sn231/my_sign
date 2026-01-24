import requests
import os
import time
import random
import re

def push_tg(token, chat_id, content):
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": content, "parse_mode": "HTML"}
    try: requests.post(url, json=data, timeout=15)
    except: pass

def get_like_tiebas(session):
    """【新增】全自动抓取你关注的贴吧"""
    print("正在获取关注列表...")
    url = "https://tieba.baidu.com/f/like/mylike"
    try:
        res = session.get(url, timeout=10)
        # 百度PC端网页是GBK编码，必须转，不然正则抓不到中文名
        html = res.content.decode('gbk', errors='ignore')
        names = re.findall(r'kw=.*?title="(.*?)"', html)
        return list(set(names)) # 去重
    except Exception as e:
        print(f"获取列表失败: {e}")
        return []

def main():
    # 保持你原来的 Secrets 读取方式
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    
    if not bduss:
        print("错误：BDUSS 配置缺失")
        return

    # 完全保留你之前能跑通的 Header
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
        print("TBS 获取失败")
        return

    # 2. 贴吧列表：如果你没填 TIEBA_NAMES，就自动去抓
    manual_names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    if manual_names:
        names = manual_names
    else:
        names = get_like_tiebas(session)

    if not names:
        print("没找到待签到的贴吧，请检查配置或关注列表")
        return

    report = [f"<b>📬 贴吧签到报告</b>", f"账号：<code>{bduss[:10]}***</code>", ""]
    
    # 3. 签到逻辑
    for name in names:
        time.sleep(random.uniform(2, 4))
        try:
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            res = session.post(url, data=data, timeout=10, allow_redirects=False)
            res_json = res.json()
            
            errno = res_json.get("no")
            if errno == 0:
                report.append(f"✅ 【{name}】 成功")
            elif errno == 1101:
                report.append(f"🔁 【{name}】 已签到")
            else:
                report.append(f"❌ 【{name}】 失败({errno})")
        except Exception as e:
            # 这里的 e 会告诉你为什么“崩溃”
            report.append(f"💥 【{name}】 异常")
            print(f"{name} 签到出错: {e}")

    # 4. 发送通知
    final_report = "\n".join(report)
    print(final_report)
    push_tg(tg_token, tg_chat_id, final_report)

if __name__ == "__main__":
    main()
