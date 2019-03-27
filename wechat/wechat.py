import json
import time
from io import BytesIO
import requests
import re
from PIL import Image
from lxml import etree

"""
author: czp
"""


class WeChatWeb(object):
    """
    模拟登陆微信网页版
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
        }
        self.session = requests.session()
        self.session.headers.update(self.headers)
        self.uuid = ""
        self.time = str(int(time.time()*1000))
        self.tip = 1
        self.redirect_uri = ""
        self.skey = ""
        self.wxsid = ""
        self.wxuin = ""
        self.pass_ticket = ""
        self.device_id = "eeeeeeeeeeeeeeee"
        self.appid = "##################"

    def get_uuid(self):
        """"
        获取uuid
        """
        url = "https://login.wx.qq.com/jslogin"
        params = {
            "appid": self.appid,
            "fun": "new",
            "lang": "zh_CN",
            "_": self.time
        }

        response = self.session.get(url=url, params=params)
        pattern = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
        res_re = re.search(pattern=pattern, string=response.text)
        # 可以根据code判断，是否获取uuid成功
        code = res_re.group(1)
        self.uuid = res_re.group(2)

    def show_qr_code(self):
        """
        展示二维码
        :return:
        """
        url = "https://login.weixin.qq.com/qrcode/" + self.uuid
        response = self.session.get(url)
        qr_code = Image.open(BytesIO(response.content))
        qr_code.show()

    def ready_for_login(self):
        """
        扫描登陆
        :return:
        """
        url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login"
        params = {
            "loginicon": "true",
            "uuid": self.uuid,
            "tip": self.tip,
            "_": self.time
        }
        response = self.session.get(url=url, params=params)
        pattern_code = r"window.code=(\d+);"
        res_re_code = re.search(pattern=pattern_code, string=response.content.decode("utf-8"))
        code = res_re_code.group(1)

        if code == "201":
            print("已扫描成功，请在手机端确认登陆")
            self.tip = 0
        elif code == "200":
            print("登陆ing====")
            pattern_uri = r'window.redirect_uri="(\S+?)";'
            res_re_uri = re.search(pattern=pattern_uri, string=response.content.decode("utf-8"))
            self.redirect_uri = res_re_uri.group(1) + "&fun=new"
        else:
            print("error")

    def login(self):
        """
        获取初始化信息
        :return:
        """
        response = self.session.get(self.redirect_uri)
        html = response.content.decode("utf-8")
        doc = etree.HTML(html)
        self.skey = doc.xpath("//skey/text()")[0]
        self.wxsid = doc.xpath("//wxsid/text()")[0]
        self.wxuin = doc.xpath("//wxuin/text()")[0]
        self.pass_ticket = doc.xpath("//pass_ticket/text()")[0]
        """
        <error>
            <ret></ret>
            <message></message>
            <skey></skey>
            <wxsid></wxsid>
            <wxuin></wxuin>
            <pass_ticket></pass_ticket>
            <isgrayscale></isgrayscale>
        </error>
        """

    def wx_init(self):
        """
        微信初始化界面信息
        :return:
        """
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r={}&lang=zh_CN&pass_ticket={}".format(
            int(time.time()), self.pass_ticket
        )

        BaseRequest = {
            "DeviceID": self.device_id,
            "Sid": self.wxsid,
            "Skey": self.skey,
            "Uin": self.wxuin
        }
        params = {
            "BaseRequest": BaseRequest
        }
        self.session.headers.update(
            {"ContentType": "application/json; charset=UTF-8"}
        )
        response = self.session.post(url=url, data=json.dumps(params))
        data = response.content.decode("utf-8")
        print(data)

    def main(self):
        self.get_uuid()
        self.show_qr_code()
        input("扫一扫: ")
        self.ready_for_login()
        self.login()
        self.wx_init()

        return self.session.cookies.get_dict()


if __name__ == '__main__':
    obj = WeChatWeb()
    obj.main()

