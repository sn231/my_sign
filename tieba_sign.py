import requests
import random
import time
import os
import json
from typing import List, Dict

# 全局配置（可通过环境变量覆盖，建议在GitHub Actions中用Secrets）
CONFIG = {
    # 推送配置（按需启用，留空则禁用对应渠道）
    "PUSHPLUS_TOKEN": os.getenv("PUSHPLUS_TOKEN", ""),  # PushPlus令牌
    "SERVERCHAN_SENDKEY": os.getenv("SERVERCHAN_SENDKEY", ""),  # Server酱SendKey
    "TG_BOT_TOKEN": os.getenv("TG_BOT_TOKEN", ""),  # Telegram Bot Token
    "TG_CHAT_ID": os.getenv("TG_CHAT_ID", ""),  # Telegram聊天ID
    # 随机延迟范围（秒），防风控
    "MIN_DELAY": 1,
    "MAX_DELAY": 3,
    # 单次获取贴吧数量（最大200，足够覆盖绝大多数用户）
    "TIEBA_PAGE_SIZE": 200
}

class TiebaSign:
    def __init__(self, bduss: str):
        self.bduss = bduss
        self.session = requests.Session()
        # 模拟手机端请求头，降低风控概率
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro Build/TQ3A.230901.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 Baidu Tieba/12.5.0.10",
            "Cookie": f"BDUSS={self.bduss}",
            "Referer": "https://tieba.baidu.com/",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.session.headers.update(self.headers)
        self.tbs = ""  # 动态获取的签到必备参数

    def _get_tbs(self) -> bool:
        """获取签到必需的tbs参数（动态更新，每次签到前需重新获取）"""
        try:
            url = "https://tieba.baidu.com/dc/common/tbs"
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            if data.get("is_login") == 1 and data.get("tbs"):
                self.tbs = data["tbs"]
                return True
            print(f"获取tbs失败，可能BDUSS失效：{data}")
            return False
        except Exception as e:
            print(f"获取tbs异常：{str(e)}")
            return False

    def get_followed_tiebas(self) -> List[str]:
        """获取账号关注的所有贴吧列表"""
        tiebas = []
        try:
            url = f"https://tieba.baidu.com/f/like/mylike?ie=utf-8&pn=0&rn={CONFIG['TIEBA_PAGE_SIZE']}"
            resp = self.session.get(url, timeout=10)
            # 解析网页中的贴吧列表（2025年该接口返回HTML，需提取关键数据）
            html = resp.text
            # 提取贴吧名称的核心逻辑（适配2025年页面结构）
            import re
            pattern = re.compile(r'class="forum_name_wrap".*?>(.*?)<\/a>')
            tieba_names = pattern.findall(html)
            if tieba_names:
                tiebas = [name.strip() for name in tieba_names if name.strip()]
            print(f"获取到关注的贴吧：{tiebas}")
        except Exception as e:
            print(f"获取关注贴吧异常：{str(e)}")
        return tiebas

    def sign_tieba(self, tieba_name: str) -> Dict[str, str]:
        """单个贴吧签到"""
        result = {
            "tieba": tieba_name,
            "status": "失败",
            "msg": ""
        }
        # 随机延迟，防风控
        delay = random.uniform(CONFIG["MIN_DELAY"], CONFIG["MAX_DELAY"])
        time.sleep(delay)
        
        if not self.tbs:
            result["msg"] = "tbs参数为空"
            return result

        try:
            url = "https://tieba.baidu.com/mo/q/newmoindex"
            params = {
                "kw": tieba_name,
                "tbs": self.tbs,
                "fid": "",
                "sign": "1"  # 签到标识
            }
            resp = self.session.post(url, data=params, timeout=10)
            data = resp.json()
            
            # 解析签到结果（适配2025年接口返回格式）
            if data.get("no") == 0:
                if data.get("data", {}).get("is_sign") == 1:
                    result["status"] = "已签到"
                    result["msg"] = "今日已签到"
                else:
                    result["status"] = "签到成功"
                    result["msg"] = f"连续签到{data.get('data', {}).get('sign_num', 0)}天"
            else:
                result["msg"] = data.get("error", "未知错误")
        except Exception as e:
            result["msg"] = f"签到异常：{str(e)}"
        
        print(f"[{tieba_name}] {result['status']} - {result['msg']}")
        return result

    def run(self) -> Dict[str, any]:
        """执行全量签到"""
        account_result = {
            "bduss": self.bduss[:10] + "****" + self.bduss[-4:],  # 脱敏显示
            "tiebas": [],
            "total": 0,
            "success": 0,
            "failed": 0,
            "already_signed": 0
        }

        # 1. 验证登录并获取tbs
        if not self._get_tbs():
            account_result["tiebas"].append({"tieba": "登录失败", "status": "失败", "msg": "BDUSS可能失效或过期"})
            return account_result

        # 2. 获取关注的贴吧
        tiebas = self.get_followed_tiebas()
        if not tiebas:
            account_result["tiebas"].append({"tieba": "无关注贴吧", "status": "提示", "msg": "未获取到关注的贴吧"})
            return account_result

        # 3. 逐个签到
        account_result["total"] = len(tiebas)
        for tb in tiebas:
            sign_res = self.sign_tieba(tb)
            account_result["tiebas"].append(sign_res)
            if sign_res["status"] == "签到成功":
                account_result["success"] += 1
            elif sign_res["status"] == "已签到":
                account_result["already_signed"] += 1
            else:
                account_result["failed"] += 1

        return account_result

def push_notify(content: str):
    """消息推送（支持PushPlus/Server酱/Telegram）"""
    # 1. PushPlus推送
    if CONFIG["PUSHPLUS_TOKEN"]:
        try:
            pushplus_url = "http://www.pushplus.plus/send"
            data = {
                "token": CONFIG["PUSHPLUS_TOKEN"],
                "title": "百度贴吧签到结果",
                "content": content,
                "template": "markdown"
            }
            requests.post(pushplus_url, json=data, timeout=10)
            print("PushPlus推送成功")
        except Exception as e:
            print(f"PushPlus推送失败：{str(e)}")

    # 2. Server酱推送（Turbo版）
    if CONFIG["SERVERCHAN_SENDKEY"]:
        try:
            serverchan_url = f"https://sctapi.ftqq.com/{CONFIG['SERVERCHAN_SENDKEY']}.send"
            data = {
                "title": "百度贴吧签到结果",
                "desp": content
            }
            requests.post(serverchan_url, data=data, timeout=10)
            print("Server酱推送成功")
        except Exception as e:
            print(f"Server酱推送失败：{str(e)}")

    # 3. Telegram推送
    if CONFIG["TG_BOT_TOKEN"] and CONFIG["TG_CHAT_ID"]:
        try:
            tg_url = f"https://api.telegram.org/bot{CONFIG['TG_BOT_TOKEN']}/sendMessage"
            data = {
                "chat_id": CONFIG["TG_CHAT_ID"],
                "text": content,
                "parse_mode": "Markdown"
            }
            requests.post(tg_url, json=data, timeout=10)
            print("Telegram推送成功")
        except Exception as e:
            print(f"Telegram推送失败：{str(e)}")

def main():
    """主函数：处理多账号签到"""
    # 从环境变量读取多账号BDUSS（逗号分隔）
    bduss_list = os.getenv("BDUSS_LIST", "").split(",")
    bduss_list = [b.strip() for b in bduss_list if b.strip()]

    if not bduss_list:
        print("未配置BDUSS_LIST环境变量，程序退出")
        return

    # 遍历所有账号签到
    all_results = []
    for bduss in bduss_list:
        print(f"\n========== 开始处理账号：{bduss[:10]}****{bduss[-4:]} ==========")
        signer = TiebaSign(bduss)
        res = signer.run()
        all_results.append(res)

    # 整理推送内容
    push_content = "# 百度贴吧自动签到结果\n"
    for res in all_results:
        push_content += f"\n### 账号：{res['bduss']}\n"
        push_content += f"- 总计贴吧：{res['total']}\n"
        push_content += f"- 签到成功：{res['success']}\n"
        push_content += f"- 已签到：{res['already_signed']}\n"
        push_content += f"- 签到失败：{res['failed']}\n"
        
        # 显示失败的贴吧
        failed_tiebas = [tb for tb in res["tiebas"] if tb["status"] == "失败"]
        if failed_tiebas:
            push_content += "- 失败列表：\n"
            for tb in failed_tiebas:
                push_content += f"  - {tb['tieba']}：{tb['msg']}\n"

    # 推送结果
    print(f"\n{push_content}")
    push_notify(push_content)

if __name__ == "__main__":
    main()
