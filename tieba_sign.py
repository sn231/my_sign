import requests
import random
import time
import os
from typing import List

class TiebaSign:
    def __init__(self, bduss: str):
        self.bduss = bduss
        self.session = requests.Session()
        # 究极伪装：全套浏览器请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
        }
        # 把 BDUSS 塞进 Cookie 桶
        self.session.cookies.set("BDUSS", self.bduss, domain="baidu.com")
        self.tbs = ""

    def check_login(self) -> bool:
        """多重验证登录状态"""
        try:
            # 打印 BDUSS 的头尾，帮你肉眼核对（中间打码）
            print(f"【调试】当前使用的 BDUSS: {self.bduss[:10]}...{self.bduss[-10:]}")
            
            # 访问个人主页来测试是否真的登录
            test_url = "https://tieba.baidu.com/f/user/json_userinfo"
            res = self.session.get(test_url, headers=self.headers, timeout=10).json()
            
            if res.get("error") == "success" or res.get("data"):
                # 如果主页能通，赶紧拿 tbs
                tbs_url = "https://tieba.baidu.com/dc/common/tbs"
                tbs_res = self.session.get(tbs_url, headers=self.headers).json()
                self.tbs = tbs_res.get("tbs")
                print(f"【成功】登录验证通过！tbs: {self.tbs}")
                return True
            
            print(f"【失败】百度坚持说你没登录。返回内容：{res}")
            return False
        except Exception as e:
            print(f"【异常】验证流程崩溃：{e}")
            return False

    def sign(self, name: str) -> str:
        time.sleep(random.uniform(3, 7)) # 模拟真人思考时间
        try:
            url = "https://tieba.baidu.com/sign/add"
            data = {"ie": "utf-8", "kw": name, "tbs": self.tbs}
            res = self.session.post(url, data=data, headers=self.headers, timeout=10).json()
            
            if res.get("no") == 0: return "签到成功"
            if res.get("no") == 1101: return "今日已签"
            return f"失败：{res.get('error')} (码:{res.get('no')})"
        except Exception as e:
            return f"崩溃：{e}"

def main():
    # 彻底解决 Secrets 读取可能存在的空格换行问题
    raw_bduss = os.getenv("BDUSS_LIST", "")
    bduss_list = [b.strip() for b in raw_bduss.replace("\n", "").split(",") if b.strip()]
    
    names = [n.strip() for n in os.getenv("TIEBA_NAMES", "").split(",") if n.strip()]

    if not bduss_list:
        print("错误：没找到 BDUSS_LIST！")
        return

    for bduss in bduss_list:
        worker = TiebaSign(bduss)
        if worker.check_login():
            print(f"准备签到名单：{names}")
            for name in names:
                print(f"  - [{name}]: {worker.sign(name)}")
        else:
            print("该账号登录验证失败，跳过。")

if __name__ == "__main__":
    main()
