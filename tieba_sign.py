import requests
import os
import time
import hashlib
import random

# 移动端签名密钥
SIGN_KEY = "tiebaclient!!!"

def calc_sign(data):
    """百度贴吧 App 协议签名算法"""
    # 1. 过滤掉值为 None 的项，将字典按 key 排序
    sorted_data = sorted([ (k, v) for k, v in data.items() if v is not None ], key=lambda x: x[0])
    # 2. 拼接 key=value 字符串
    sign_str = "".join([f"{k}={v}" for k, v in sorted_data])
    # 3. 加上密钥并计算 MD5
    sign_str += SIGN_KEY
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def push_tg(token, chat_id, content):
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": content, "parse_mode": "HTML"}
    try: requests.post(url, json=data, timeout=15)
    except: pass

def get_like_list(session, bduss):
    """【App协议】获取关注列表"""
    print("正在通过 App 协议获取关注列表...")
    # 改用 HTTPS 保证稳定性
    url = "https://c.tieba.baidu.com/c/f/forum/like"
    data = {
        'BDUSS': bduss,
        '_client_id': 'wappc_1534235498291_488',
        '_client_type': '2',
        '_client_version': '9.7.8.0',
        'from': '1008621y',
        'model': 'MI+5',
        'net_type': '1',
        'page_no': '1',
        'page_size': '200',
        'timestamp': str(int(time.time())),
    }
    data['sign'] = calc_sign(data)

    try:
        res = session.post(url, data=data, timeout=10).json()
        names = []
        forum_list = res.get("forum_list", {})
        # 合并普通吧和官方吧
        for category in ["non-gconforum", "gconforum"]:
            forums = forum_list.get(category, [])
            for f in forums:
                if f.get("name"):
                    names.append(f.get("name"))
        print(f"成功获取到 {len(names)} 个贴吧")
        return names
    except Exception as e:
        print(f"获取列表异常: {e}")
        return []

def main():
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()
    
    if not bduss:
        print("错误：BDUSS 未配置")
        return

    # 使用统一 Session
    session = requests.Session()
    # 模拟手机端 Header
    session.headers.update({
        "User-Agent": "bdtb for Android 9.7.8.0",
        "Content-Type": "application/x-www-form-urlencoded"
    })

    # 1. 获取 tbs
    try:
        tbs_res = session.get(f"https://tieba.baidu.com/dc/common/tbs?BDUSS={bduss}").json()
        tbs = tbs_res.get("tbs")
    except:
        tbs = None

    if not tbs:
        print("TBS 获取失败，BDUSS 可能失效")
        return

    # 2. 获取列表
    manual_names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    names = manual_names if manual_names else get_like_list(session, bduss)

    if not names:
        print("未发现待签到贴吧")
        return

    report = [f"<b>📬 贴吧签到报告</b>", f"账号：<code>{bduss[:10]}***</code>", ""]
    
    # 3. 签到
    sign_url = "https://c.tieba.baidu.com/c/c/forum/sign"
    
    for name in names:
        time.sleep(random.uniform(2, 4))
        try:
            # 补齐所有 App 协议参数，确保签名绝对正确
            sign_data = {
                'BDUSS': bduss,
                '_client_id': 'wappc_1534235498291_488',
                '_client_type': '2',
                '_client_version': '9.7.8.0',
                'from': '1008621y',
                'kw': name,
                'model': 'MI+5',
                'net_type': '1',
                'tbs': tbs,
                'timestamp': str(int(time.time())),
            }
            sign_data['sign'] = calc_sign(sign_data)
            
            res = session.post(sign_url, data=sign_data, timeout=10).json()
            # 统一转为字符串进行判断
            err_code = str(res.get("error_code", ""))
            
            if err_code == "0":
                report.append(f"✅ 【{name}】 成功 (+6exp)")
            elif err_code in ["1101", "160002", "20004"]:
                report.append(f"🔁 【{name}】 已签到")
            elif err_code in ["5", "257"]:
                report.append(f"⚠️ 【{name}】 需验证码")
            elif err_code == "1990055":
                report.append(f"❌ 【{name}】 Cookie失效")
                break
            else:
                msg = res.get("error_msg") or "未知原因"
                report.append(f"❌ 【{name}】 失败({err_code}: {msg})")
        except Exception as e:
            report.append(f"💥 【{name}】 程序崩溃")

    final_report = "\n".join(report)
    print(final_report)
    push_tg(tg_token, tg_chat_id, final_report)

if __name__ == "__main__":
    main()
