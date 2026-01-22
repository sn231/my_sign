import requests
import random
import time
import os
import re
from typing import List, Dict

class TiebaSign:
    def __init__(self, bduss: str):
        self.bduss = bduss
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": f"BDUSS={self.bduss}",
            "Referer": "https://tieba.baidu.com/",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        self.session.headers.update(self.headers)
        self.tbs = ""

    def get_tbs(self) -> bool:
        """获取签到必须的 tbs 参数"""
        try:
            url = "https://tieba.baidu.com/dc/common/tbs"
            res = self.session.get(url, timeout=10).json()
            if res.get("is_login") == 1:
                self.tbs = res.get("tbs")
                return True
            print(f"【错误】BDUSS 可能已失效，请重新抓取。返回结果：{res}")
            return False
        except Exception as e:
            print(f"【异常】获取 tbs 失败：{e}")
            return False

    def get_tiebas(self) -> List[str]:
        """获取贴吧名单：优先从环境变量 TIEBA_NAMES 读取"""
        manual = os.getenv("TIEBA_NAMES", "")
        if manual:
            return [n.strip() for n in manual.split(",") if n.strip()]
        return []

    def sign(self, name: str) -> str:
        """核心签到逻辑"""
        # 随机延迟，防止被抓
        time.sleep(random.uniform(2, 5))
        try:
            # 使用网页版签到接口，这个接口目前对 BDUSS 登录最友好
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": self.tbs}
            res = self.session.post(url, data=data, timeout=10).json()
            
            # 这里的逻辑涵盖了所有可能的情况
            if res.get("no") == 0:
                return "签到成功"
            elif res.get("no") == 1101:
                return "已签到"
            elif res.get("no") == 2150040:
                return "需要验证码（脚本暂时无法处理）"
            else:
                return f"失败：{res.get('error', '未知原因')} (错误码:{res.get('no')})"
        except Exception as e:
            return f"请求崩溃：{e}"

def main():
    bduss_list = [b.strip() for b in os.getenv("BDUSS_LIST", "").split(",") if b.strip()]
    if not bduss_list:
        print("未检测到 BDUSS_LIST，请检查 Secrets 配置。")
        return

    for bduss in bduss_list:
        print(f"\n>>> 正在处理账号：{bduss[:10]}***")
        worker = TiebaSign(bduss)
        if not worker.get_tbs():
            continue
            
        names = worker.get_tiebas()
        if not names:
            print("未配置贴吧名单 TIEBA_NAMES。")
            continue
            
        print(f"待签到名单：{names}")
        for name in names:
            result = worker.sign(name)
            print(f"  - [{name}]: {result}")

if __name__ == "__main__":
    main()
