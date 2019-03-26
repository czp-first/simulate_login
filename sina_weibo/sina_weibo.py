import json
from fake_useragent import UserAgent
import requests
import base64
import rsa
import binascii
import re
from urllib.parse import quote


def m_login(username, password):
    url = "https://passport.weibo.cn/sso/login"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://passport.weibo.cn",
        "Referer": "https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F",
        "User-Agent": UserAgent().random
    }

    data = {
        "username": username,
        "password": password,
        "savestate": "1",
        "ec": "0",
        "pagerefer": "https://m.weibo.cn/login?backURL=https%253A%252F%252Fm.weibo.cn%252F",
        "entry": "mweibo",
        "mainpageflag": "1"
    }

    response = requests.post(url=url, headers=headers, data=data)

    with open("../cookies.txt", "w") as f:
        f.write(json.dumps(response.cookies.get_dict()))

    return response.cookies


def pc_login(username, password):

    # 读取preinfo.php, 获取servertime, nonce, pubkey, rsakv
    def get_prelogin_info():
        url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.20)"
        html = requests.get(url).text
        json_str = re.findall(r'\((\{.*?\})\)', html)[0]
        data = json.loads(json_str)
        servertime = data["servertime"]
        nonce = data["nonce"]
        pubkey = data["pubkey"]
        rsakv = data["rsakv"]
        print(servertime, nonce, pubkey, rsakv)
        return servertime, nonce, pubkey, rsakv

    # 使用base64对username进行编码
    def encode_username(username):
        username_ = quote(username)
        print(base64.encodestring(username_.encode("utf-8"))[:-1])
        return base64.encodestring(username_.encode("utf-8"))[:-1]

    # 使用rsa2对password进行编码
    def encode_password(password, servertime, nonce, pubkey):
        rsa_pubkey = int(pubkey, 16)
        RSAKey = rsa.PublicKey(rsa_pubkey, 65537)
        code_str = str(servertime) + "\t" + str(nonce) + "\n" + str(password)
        pwd = rsa.encrypt(code_str.encode("utf-8"), RSAKey)
        print(binascii.b2a_hex(pwd))
        return binascii.b2a_hex(pwd)

    # 构造请求参数
    def encode_post_data(username, password, servertime, nonce, pubkey, rsakv):
        su = encode_username(username)
        sp = encode_password(password, servertime, nonce, pubkey)

        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "qrcode_flag": "false",
            "useticket": "1",
            "pagerefer": "https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1",
            "vsnf": "1",
            "su": su,
            "service": "miniblog",
            "servertime": servertime,
            "nonce": nonce,
            "pwencode": "rsa2",
            "rsakv": rsakv,
            "sp": sp,
            "sr": "1440*900",
            "encoding": "UTF-8",
            "prelt": "163",
            "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        return post_data

    servertime, nonce, pubkey, rsakv = get_prelogin_info()
    post_data = encode_post_data(username, password, servertime, nonce, pubkey, rsakv)
    login_url = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"

    login_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "login.sina.com.cn",
        "Origin": "https://weibo.com",
        "Referer": "https://weibo.com/",
        "User-Agent": UserAgent().random
    }

    session = requests.session()
    # session.headers = login_headers
    session.post(url=login_url, data=post_data)
    with open("index.html", "w") as f:
        res = session.get("https://weibo.com/u/3191997705/home", headers=login_headers)
        f.write(res.text)
    session.close()


if __name__ == '__main__':
    username = input("please input sina weibo username: ")
    password = input("please input sina weibo password: ")
    # m_login(username, password)
    pc_login(username, password)
