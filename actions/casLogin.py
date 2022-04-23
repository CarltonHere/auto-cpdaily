import re
import requests
import urllib.parse
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from actions.utils import Utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class casLogin:
    # 初始化cas登陆模块
    def __init__(self, username, password, login_url, host, session):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.host = host
        self.session = session
        self.type = 0
        self.headers = {
            'User-Agent':
            'Mozilla/5.0 (Linux; Android 8.0.0; MI 6 Build/OPR1.170623.027; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 okhttp/3.12.4',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    # 判断是否需要验证码
    def getNeedCaptchaUrl(self):
        if self.type == 0:
            url = self.host + 'authserver/needCaptcha.html' + '?username=' + self.username
            flag = self.session.get(url, verify=False).text
            return 'false' != flag[:5] and 'False' != flag[:5]
        else:
            url = self.host + 'authserver/checkNeedCaptcha.htl' + '?username=' + self.username
            flag = self.session.get(url, verify=False).json()
            return flag['isNeed']

    def login(self):
        html = self.session.get(self.login_url, verify=False).text
        soup = BeautifulSoup(html, 'html.parser')
        if len(soup.select('#casLoginForm')) > 0:
            self.type = 0
        elif len(soup.select('#loginFromId')) > 0:
            soup = BeautifulSoup(str(soup.select('#loginFromId')[1]), 'html.parser')
            self.type = 1
        elif len(soup.select('#fm1')) > 0:
            soup = BeautifulSoup(str(soup.select('#fm1')[0]), 'html.parser')
            self.type = 2
        else:
            raise Exception('出错啦！网页中没有找到LoginForm')

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

        # 获取密钥
        if self.type == 2:
            pattern = 'RSAKeyPair\((.*?)\);'
            publicKey = re.findall(pattern, html)
            publicKey = publicKey[0].replace('"', "").split(',')
            params['password'] = Utils.encryptRSA(self.password, publicKey[2],
                                                  publicKey[0])
            params['captcha'] = Utils.getCodeFromImg(
                self.session, self.host + 'lyuapServer/captcha.jsp')
        else:
            if self.type == 0:
                salt = soup.select("#pwdDefaultEncryptSalt")
            else:
                salt = soup.select("#pwdEncryptSalt")
            if len(salt) != 0:
                salt = salt[0].get('value')
            else:
                pattern = '\"(\w{16})\"'
                salt = re.findall(pattern, html)
                if len(salt) == 1:
                    salt = salt[0]
                else:
                    salt = False
            if not salt:
                params['password'] = self.password
            else:
                params['password'] = Utils.encryptAES(
                    Utils.randString(64) + self.password, salt)
            if self.getNeedCaptchaUrl():
                if self.type == 0:
                    imgUrl = self.host + 'authserver/captcha.html'
                    params['captchaResponse'] = Utils.getCodeFromImg(
                        self.session, imgUrl)
                else:
                    imgUrl = self.host + 'authserver/getCaptcha.htl'
                    params['captcha'] = Utils.getCodeFromImg(
                        self.session, imgUrl)
        data = self.session.post(self.login_url,
                                 data=urllib.parse.urlencode(params),
                                 headers=self.headers,
                                 allow_redirects=False)
        # 如果等于302强制跳转，代表登陆成功
        if data.status_code == 302:
            jump_url = data.headers['Location']
            res = self.session.post(jump_url, verify=False)
            if res.url.find('campusphere.net/') == -1:
                raise Exception('CAS登陆失败,未能成功跳转今日校园!')
            return self.session.cookies
        elif data.status_code == 200 or data.status_code == 401:
            data = data.text
            soup = BeautifulSoup(data, 'html.parser')
            if len(soup.select('#errorMsg')) > 0:
                msg = soup.select('#errorMsg')[0].get_text()
            elif len(soup.select('#formErrorTip2')) > 0:
                msg = soup.select('#formErrorTip2')[0].get_text()
            elif len(soup.select('#msg')) > 0:
                msg = soup.select('#msg')[0].get_text()
            else:
                msg = 'CAS登陆失败,意料之外的错误!'
            raise Exception(msg)
        else:
            raise Exception('CAS登陆失败！返回状态码：' + str(data.status_code))
