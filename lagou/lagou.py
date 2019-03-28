import json

import requests
import re
import hashlib
import time
from PIL import Image
from io import BytesIO


"""
author: czp
"""


class LaGou(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
        }
        self.session.headers.update(self.headers)
        self.geetest = ""
        self.token = ""
        self.code = ""

    def get_token_code(self):
        """
        从登陆页面源码获取token，code
        :return:
        """
        url = "https://passport.lagou.com/login/login.html"
        response = self.session.get(url=url)
        html = response.content.decode("utf-8")
        """
        <!-- 页面样式 -->
        <!-- 动态token，防御伪造请求，重复提交 -->
        <script>
            window.X_Anti_Forge_Token = '91454c4e-210c-4da5-b690-fd954a1d7d1d';
            window.X_Anti_Forge_Code = '17529022';
        </script>
        """
        pattern_token = re.compile(r"window.X_Anti_Forge_Token = '(.+?)';")
        pattern_code = re.compile(r"window.X_Anti_Forge_Code = '(.+?)';")
        self.token = pattern_token.search(html).group(1)
        self.code = pattern_code.search(html).group(1)
        print(self.token, self.code)

    def encode_password(self):
        """
        var c, g = C.collectData(), v = "veenike";
        g.password = md5(g.password),
        g.password = md5(v + g.password + v),
        a && (g.challenge = a),
        $.ajax({
            url: window.GLOBAL_DOMAIN.pctx + "/login/login.json",
            data: g,
            type: "post",
            dataType: "json",
            cache: !1
        })
        :return:
        """
        self.password = "veenike" + hashlib.md5(self.password.encode("utf-8")).hexdigest() + "veenike"
        self.password = hashlib.md5(self.password.encode("utf-8")).hexdigest()

    def get_vcode(self):
        url = f"https://passport.lagou.com/vcode/create?from=register&refresh={str(int(time.time()))}"
        response = self.session.get(url)
        vcode = Image.open(BytesIO(response.content))
        vcode.show()
        self.geetest = input("请输入验证码: ").center(20, ">")

    def login(self):
        data = {
            "isValidate": "true",
            "username": self.username,
            "password": self.password,
            "request_form_verifyCode": self.geetest,
            "submit": ""
        }
        url = "https://passport.lagou.com/login/login.json"
        headers = {
            "Referer": "https://passport.lagou.com/login/login.html",
            "X-Anit-Forge-Code": self.code,
            "X-Anit-Forge-Token": self.token,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
        }
        response = self.session.post(url=url, data=data, headers=headers)
        print(response.content.decode("utf-8"))
        data = json.loads(response.content.decode("utf-8"))
        if data.get("state") == 1:
            print("yes")
        elif data.get("state") == 21010:
            # self.get_vcode()
            # self.login()
            pass

    def main(self):
        self.get_token_code()
        self.encode_password()
        self.login()


if __name__ == '__main__':
    username = input("username: ")
    password = input("password: ")
    obj = LaGou(username, password)
    obj.main()
