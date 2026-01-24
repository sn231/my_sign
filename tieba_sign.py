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
    """自动获取你关注的贴吧列表 - 强化版"""
    print("正在获取关注列表...")
    tiebas = []
    # 爬取前 3 页，防止你关注的吧太多
    for page in range(1, 4):
        url = f"https://tieba.baidu.com/f/like/mylike?&pn={page}"
        try:
            res = session.get(url, timeout=15)
            # 关键点：百度PC端是 GBK 编码，不转码正则会失效
            res.encoding = 'gbk' 
            html = res.text
            
            # 更精确的正则：匹配 <a> 标签且在 kw= 路径下的 title
            # 格式通常是 <a href="/f?kw=xxx" title="贴吧名">
            found = re.findall(r'kw=.*?title="(.*?)"', html)
            if not found:
                break
            tiebas.extend(found)
            time.sleep(1) # 别抓太快
        except Exception as e:
            print(f"第 {page} 页获取失败: {e}")
            break
            
    # 去重
    unique_tiebas = list(set(tiebas))
    print(f"成功获取到 {len(unique_tiebas)} 个贴吧")
    return unique_tiebas

def main():
    # 从 Secrets 获取 BDUSS
    bduss_env = os.getenv("BDUSS_LIST", "").strip()
    if not bduss_env:
        print("错误：BDUSS_LIST 未配置")
        return
    
    bduss = bduss_env.split(",")[0].strip()
    tg_token = os.getenv("TG_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TG_CHAT_ID", "").strip()

    session = requests.Session()
    # 模拟一个更真实的浏览器
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"BDUSS={bduss};",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    })

    # 1. 获取 tbs (必须步骤)
    try:
        tbs_data = session.get("https://tieba.baidu.com/dc/common/tbs").json()
        tbs = tbs_data.get("tbs")
        if not tbs or tbs_data.get("is_login") == 0:
            print("TBS 获取失败，BDUSS 可能过期")
            push_tg(tg_token, tg_chat_id, "❌ 贴吧签到：BDUSS 已失效，请更新 Secret")
            return
    except:
        print("获取 TBS 异常")
        return

    # 2. 获取贴吧列表
    # 依然保留 TIEBA_NAMES 覆盖功能
    manual_names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    if manual_names:
        names = manual_names
        print(f"使用手动配置的 {len(names)} 个贴吧")
    else:
        names = get_like_tiebas(session)

    if not names:
        print("警告：没有找到任何待签到的贴吧")
        return

    report = [f"<b>📬 贴吧签到报告 (2026版)</b>", f"账号：<code>{bduss[:10]}***</code>", f"总数：{len(names)}", ""]
    
    # 3. 开始签到
    for name in names:
        # 别签太快，容易被百度封 API
        time.sleep(random.uniform(2, 5))
        try:
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            res = session.post(url, data=data, timeout=10).json()
            
            errno = res.get("no")
            if errno == 0:
                report.append(f"✅ 【{name}】 成功")
            elif errno == 1101:
                report.append(f"🔁 【{name}】 已签到")
            else:
                report.append(f"❌ 【{name}】 失败({errno})")
                print(f"贴吧 {name} 返回详细信息: {res}")
        except Exception as e:
            report.append(f"💥 【{name}】 异常")
            print(f"签到 {name} 时发生程序崩溃: {e}")

    final_report = "\n".join(report)
    print(final_report)
    push_tg(tg_token, tg_chat_id, final_report)

if __name__ == "__main__":
    main()
