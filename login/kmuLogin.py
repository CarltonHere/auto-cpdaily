import re
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from login.Utils import Utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class kmuLogin:
    # 初始化cas登陆模块
    def __init__(self, username, password, login_url, host, session):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.host = host
        self.session = session

    def login(self):
        html = self.session.get(self.login_url, verify=False).text
        soup = BeautifulSoup(html, 'lxml')
        form = soup.select('#fm1')
        if (len(form) == 0):
            raise Exception('出错啦！网页中没有找到LoginForm')
        soup = BeautifulSoup(str(form[0]), 'lxml')
        # 填充数据
        params = {}
        form = soup.select('input')
        for item in form:
            if None != item.get('name') and len(item.get('name')) > 0:
                if item.get('name') != 'rememberMe':
                    if None == item.get('value'):
                        params[item.get('name')] = ''
                    else:
                        params[item.get('name')] = item.get('value')
        params['username'] = self.username
        pattern = 'RSAKeyPair\((.*?)\);'
        publicKey = re.findall(pattern, html)
        publicKey = publicKey[0].replace('"', "").split(',')
        params['password'] = Utils.encryptRSA(self.password, publicKey[2],
                                              publicKey[0])
        imgUrl = self.host + 'lyuapServer/captcha.jsp'
        params['captcha'] = Utils.getCodeFromImg(self.session, imgUrl)
        data = self.session.post(self.login_url,
                                 params=params,
                                 allow_redirects=False)
        # 如果等于302强制跳转，代表登陆成功
        if data.status_code == 302:
            jump_url = data.headers['Location']
            self.session.post(jump_url, verify=False)
            return self.session.cookies
        elif data.status_code == 200:
            data = data.text
            soup = BeautifulSoup(data, 'lxml')
            msg = soup.select('#msg')[0].get_text()
            raise Exception(msg)
        else:
            raise Exception('CAS登陆失败！返回状态码：' + str(data.status_code))