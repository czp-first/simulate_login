import json
import time
from selenium import webdriver


def test_cookie(url1, url2):
    driver = webdriver.Chrome()
    driver.delete_all_cookies()
    with open("cookies.txt", "r") as f:
        cookies = json.loads(f.read())
    driver.get(url1)
    time.sleep(5)
    for cookie in cookies.items():
        driver.add_cookie({"name": cookie[0], "value": cookie[1]})
    driver.get(url2)
    time.sleep(20)
    driver.close()


if __name__ == '__main__':
    url1 = "https://weibo.com/"
    url2 = "https://weibo.com/u/3191997705/home"
    test_cookie(url1, url2)
