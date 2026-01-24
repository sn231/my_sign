import requests
import os
import time
import random

def push_tg(token, chat_id, content):
    """结果推送到 Telegram"""
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": content, "parse_mode": "HTML"}
    try: requests.post(url, json=data, timeout=15)
    except: pass

def get_like_tiebas(session):
    """【App协议版】获取关注列表 - 返回纯净 JSON"""
    print("正在获取关注列表...")
    # 使用文档推荐的移动端接口和 RN=50 参数
    url = "https://tieba.baidu.com/f/like/mylike?rn=50"
    try:
        res = session.get(url, timeout=10).json()
        if res.get("error") == 0 or res.get("no") == 0:
            # 兼容不同版本的字段名
            data = res.get("data", {})
            tieba_list = data.get("like_forum", [])
            names = [item.get("forum_name") for item in tieba_list if item.get("forum_name")]
            print(f"成功获取到 {len(names)} 个贴吧")
            return names
        else:
            print(f"获取列表失败，原因：{res.get('errmsg', '未知')}")
            return []
    except Exception as e:
        print(f"获取列表异常: {e}")
        return []

def main():
    # 1. 初始化配置
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    
    if not bduss:
        print("错误：BDUSS 配置缺失")
        return

    # 2. 核心：使用移动端 UA (这是获取 JSON 的关键)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 9 SE) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.130 Mobile Safari/537.36 Tieba/12.5.0.12",
        "Cookie": f"BDUSS={bduss};",
        "Referer": "https://tieba.baidu.com/"
    })

    # 3. 获取 TBS 动态校验码
    try:
        tbs_res = session.get("https://tieba.baidu.com/dc/common/tbs", timeout=10).json()
        tbs = tbs_res.get("tbs")
    except:
        tbs = None

    if not tbs:
        print("TBS 获取失败，可能 BDUSS 已过期")
        return

    # 4. 确定签到名单
    manual_names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    if manual_names:
        names = manual_names
        print(f"使用手动配置的 {len(names)} 个贴吧")
    else:
        names = get_like_tiebas(session)

    if not names:
        print("未获取到任何待签到贴吧")
        return

    report = [f"<b>📬 贴吧签到报告 (App协议版)</b>", f"账号：<code>{bduss[:10]}***</code>", ""]
    
    # 5. 执行签到
    for name in names:
        time.sleep(random.uniform(2, 4)) # 严格遵守文档建议的频率控制
        try:
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            res = session.post(url, data=data, timeout=10).json()
            
            no = res.get("no")
            if no == 0:
                report.append(f"✅ 【{name}】 成功")
            elif no == 1101:
                report.append(f"🔁 【{name}】 今日已签")
            elif no == 160002:
                report.append(f"⚠️ 【{name}】 需验证码")
            else:
                msg = res.get("errmsg") or res.get("error") or "未知错误"
                report.append(f"❌ 【{name}】 失败({no}: {msg})")
        except:
            report.append(f"💥 【{name}】 程序崩溃")

    # 6. 推送
    final_report = "\n".join(report)
    print(final_report)
    push_tg(tg_token, tg_chat_id, final_report)

if __name__ == "__main__":
    main()
