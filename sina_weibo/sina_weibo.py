import json
from fake_useragent import UserAgent
import requests
import base64
import rsa
import binascii
import re
from urllib.parse import quote
import urllib.request


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
    data = urllib.parse.urlencode(post_data).encode("utf-8")
    login_url_one = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"

    pattern_one = re.compile('location\.replace\("(.*?)"\)')
    pattern_two = re.compile("location\.replace\('(.*?)'\)")
    pattern_three = re.compile(r'"userdomain":"(.*?)"')

    login_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }

    session = requests.session()
    session.headers.update(login_headers)
    session.get("http://weibo.com/login.php")
    response_one = session.post(url=login_url_one, data=post_data, headers=login_headers)
    login_url_two = pattern_one.search(response_one.text).group(1)
    response_two = session.get(url=login_url_two)
    login_url_three = pattern_two.search(response_two.text).group(1)
    response_three = session.get(url=login_url_three, headers=login_headers)
    login_url = "http://weibo.com/" + pattern_three.search(response_three.text).group(1)
    response = session.get(login_url, headers=login_headers)

    return session.cookies.get_dict()

if __name__ == '__main__':
    username = input("please input sina weibo username: ")
    password = input("please input sina weibo password: ")
    # m_login(username, password)
    pc_login(username, password)
