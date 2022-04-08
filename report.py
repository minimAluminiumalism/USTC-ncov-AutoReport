# encoding=utf8
import requests
import json
import time
import datetime
import pytz
import re
import sys
import argparse
from bs4 import BeautifulSoup


class Report(object):
    def __init__(self, stuid, password, data_path):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path
        self.login_page_url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'

    def report(self):
        loginsuccess = False
        retrycount = 5
        while (not loginsuccess) and retrycount:
            session = self.login()
            cookies = session.cookies
            getform = session.get("http://weixine.ustc.edu.cn/2020")
            retrycount = retrycount - 1
            if getform.url != "https://weixine.ustc.edu.cn/2020/home":
                print("Login Failed! Retry...")
            else:
                print("Login Successful!")
                loginsuccess = True
        print(loginsuccess)
        if not loginsuccess:
            return False
        data = getform.text
        data = data.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']
        with open(self.data_path, "r+") as f:
            data = f.read()
            data = json.loads(data)
            data["_token"] = token

        headers = {
            'authority': 'weixine.ustc.edu.cn',
            'origin': 'http://weixine.ustc.edu.cn',
            'upgrade-insecure-requests': '1',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'http://weixine.ustc.edu.cn/2020/',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Connection': 'close',
            'cookie': 'PHPSESSID=' + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get(
                "XSRF-TOKEN") + ";laravel_session=" + cookies.get("laravel_session"),
        }
        url = "https://weixine.ustc.edu.cn/2020/daliy_report"
        response = session.post(url, data=data, headers=headers)
        if response.status_code == 200 and "上报成功" in response.text:
            print("Daily report successfully.")
            return True
        return False

    def login(self):
        r = requests.get(self.login_page_url)
        init_cookie = r.headers['Set-Cookie'].split(';')[0]
        soup = BeautifulSoup(r.text, 'lxml')
        cas_lt = soup.find('input', id="CAS_LT")['value']

        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Referer': 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin',
            'Cookie': '{}; lang=zh'.format(init_cookie),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'model': 'uplogin.jsp',
            'CAS_LT': cas_lt,
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'username': self.stuid,
            'password': self.password,
            'warn': '',
            'showCode': '',
            'button': ''
        }
        session = requests.Session()
        login_url = "https://passport.ustc.edu.cn/login"
        r = session.post(login_url, data=data, headers=headers)
        print("login...")
        return session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='URC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    args = parser.parse_args()
    autorepoter = Report(stuid=args.stuid, password=args.password, data_path=args.data_path)
    count = 5
    while count != 0:
        ret = autorepoter.report()
        if ret != False:
            break
        print("Report Failed, retry...")
        count = count - 1
    if count != 0:
        exit(0)
    else:
        exit(-1)
