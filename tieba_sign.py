import requests
import os
import time
import hashlib
import random

def push_tg(token, chat_id, content):
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": content, "parse_mode": "HTML"}
    try: requests.post(url, json=data, timeout=15)
    except: pass

def get_like_list(bduss):
    """【App协议】只负责拿列表，解决新关注贴吧显示问题"""
    print("正在获取关注列表...")
    # 这里用 App 的签名算法，保证能拿到最全的 200 个吧，且没乱码
    url = "https://c.tieba.baidu.com/c/f/forum/like"
    data = {
        'BDUSS': bduss,
        '_client_id': 'wappc_1534235498291_488',
        '_client_type': '2',
        '_client_version': '9.7.8.0',
        'from': '1008621y',
        'timestamp': str(int(time.time())),
    }
    # 算个签名，只为了拿列表
    sign_str = "".join([f"{k}={v}" for k, v in sorted(data.items())]) + "tiebaclient!!!"
    data['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    try:
        res = requests.post(url, data=data, timeout=10).json()
        names = []
        forum_list = res.get("forum_list", {})
        for category in ["non-gconforum", "gconforum"]:
            for f in forum_list.get(category, []):
                if f.get("name"): names.append(f.get("name"))
        return names
    except:
        return []

def main():
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    
    if not bduss: return

    # --- 这里完全照抄你最早能跑通的 Session 配置 ---
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"BDUSS={bduss};",
        "Referer": "https://tieba.baidu.com/"
    })

    # 1. 拿 tbs (照抄你最早的代码)
    try:
        tbs_res = session.get("https://tieba.baidu.com/dc/common/tbs", timeout=10).json()
        tbs = tbs_res.get("tbs")
    except:
        tbs = None
    if not tbs: return

    # 2. 确定名单 (缝合点：如果是空就自动获取)
    manual_names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    names = manual_names if manual_names else get_like_list(bduss)

    report = [f"<b>📬 贴吧签到报告</b>", f"账号：<code>{bduss[:10]}***</code>", ""]
    
    # 3. 签到逻辑 (完全还原你最早的逻辑，只改了判断，区分已签到)
    for name in names:
        time.sleep(random.uniform(2, 4))
        try:
            # 这里的接口地址和你最早的代码一模一样
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            res = session.post(url, data=data, timeout=10, allow_redirects=False)
            res_json = res.json()
            
            # 改进判断逻辑：区分 0(成功) 和 1101(已签到)
            errno = res_json.get("no")
            if errno == 0:
                report.append(f"✅ 【{name}】 成功")
            elif errno == 1101:
                report.append(f"🔁 【{name}】 已签到")
            else:
                report.append(f"❌ 【{name}】 失败({errno})")
        except:
            # 针对你提到的【数据结构】崩溃问题，这里捕获异常
            report.append(f"💥 【{name}】 异常")

    final_report = "\n".join(report)
    print(final_report)
    push_tg(tg_token, tg_chat_id, final_report)

if __name__ == "__main__":
    main()
