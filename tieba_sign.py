import requests
import os
import time
import random

def main():
    # 1. 准备工作
    bduss = os.getenv("BDUSS_LIST", "").strip().split(",")[0].strip()
    names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]
    
    if not bduss or not names:
        print("错误：Secrets 没填对，请检查 BDUSS_LIST 或 TIEBA_NAMES")
        return

    # 2. 核心伪装
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"BDUSS={bduss};", # 只带这一个最重要的
        "Referer": "https://tieba.baidu.com/"
    })

    print(f">>> 正在尝试直接签到，名单：{names}")

    # 3. 先拿一个关键参数 tbs (这个不应该被重定向)
    try:
        tbs_res = session.get("https://tieba.baidu.com/dc/common/tbs", timeout=10).json()
        tbs = tbs_res.get("tbs")
        if not tbs:
            print(f"无法获取 tbs，百度返回：{tbs_res}")
            return
        print(f"成功拿到通行证(tbs): {tbs}")
    except Exception as e:
        print(f"拿到 tbs 时崩了：{e}")
        return

    # 4. 开始暴力签到
    for name in names:
        time.sleep(random.uniform(2, 4))
        try:
            # allow_redirects=False 是关键：不许百度乱跳！
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": tbs}
            res = session.post(url, data=data, timeout=10, allow_redirects=False)
            
            if res.status_code == 200:
                json_data = res.json()
                if json_data.get("no") == 0:
                    print(f"  - [{name}]: 签到成功！")
                elif json_data.get("no") == 1101:
                    print(f"  - [{name}]: 今日已签过。")
                else:
                    print(f"  - [{name}]: 失败，原因：{json_data.get('error')}")
            elif res.status_code == 302:
                print(f"  - [{name}]: 失败。百度把你踢到了验证页面：{res.headers.get('Location')}")
            else:
                print(f"  - [{name}]: 接口返回了奇怪的状态码：{res.status_code}")
                
        except Exception as e:
            print(f"  - [{name}]: 签到时异常：{e}")

if __name__ == "__main__":
    main()
