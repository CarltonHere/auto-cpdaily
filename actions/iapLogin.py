import json
import requests
from urllib3.exceptions import InsecureRequestWarning
from actions.utils import Utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class iapLogin:
    # 初始化iap登陆类
    def __init__(self, username, password, login_url, host, session):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.host = host
        self.session = session
        self.ltInfo = None
        self.count = 0

    # 判断是否需要验证码
    def getNeedCaptchaUrl(self):
        data = self.session.post(
            f'{self.host}iap/checkNeedCaptcha?username={self.username}',
            data=json.dumps({}),
            verify=False).json()
        return data['needCaptcha']

    def login(self):
        params = {}
        self.ltInfo = self.session.post(f'{self.host}iap/security/lt',
                                        data=json.dumps({})).json()
        params['lt'] = self.ltInfo['result']['_lt']
        params['rememberMe'] = 'false'
        params['dllt'] = ''
        params['mobile'] = ''
        params['username'] = self.username
        params['password'] = self.password
        needCaptcha = self.getNeedCaptchaUrl()
        if needCaptcha:
            imgUrl = f'{self.host}iap/generateCaptcha?ltId={self.ltInfo["result"]["_lt"]}'
            code = Utils.getCodeFromImg(self.session, imgUrl)
            params['captcha'] = code
        else:
            params['captcha'] = ''
        data = self.session.post(f'{ self.host }iap/doLogin',
                                 params=params,
                                 verify=False,
                                 allow_redirects=False)
        if data.status_code == 302:
            data = self.session.post(data.headers['Location'], verify=False)
            return self.session.cookies
        else:
            data = data.json()
            self.count += 1
            if data['resultCode'] == 'CAPTCHA_NOTMATCH':
                if self.count < 10:
                    self.login()
                else:
                    raise Exception('验证码错误超过10次，请检查')
            elif data['resultCode'] == 'FAIL_UPNOTMATCH':
                raise Exception('用户名密码不匹配，请检查')
            else:
                raise Exception(f'登陆出错，状态码：{ data["resultCode"]}，请联系开发者修复...')
