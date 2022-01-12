import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header


# 消息通知聚合类
class pushKit:
    # 初始化类
    def __init__(self, option):
        self.option = option
        self.type = option['method']

    def sendMsg(self, title, msg, user=''):
        if 'notifyOption' not in user:
            return '该用户未配置推送,已取消发送！'
        if 'rcvAcc' not in user['notifyOption']:
            return '该用户未配置推送,已取消发送！'
        if user['notifyOption']['rcvAcc'] == "":
            return '该用户未配置推送,已取消发送！'

        userOption = user['notifyOption']
        # 获取接收账号
        rcvAcc = userOption['rcvAcc']
        # 获取全局推送模式
        method = self.type
        # 获取用户指定的推送模式
        if 'method' in userOption:
            method = userOption['method']

        # 判断推送类型
        if method == 0:
            return '消息推送服务未启用'
        if method == 1:
            return self.sendMsgByMailApi(rcvAcc, title, msg)
        if method == 2:
            return self.sendMsgBySmtp(rcvAcc, title, msg)
        if method == 3:
            return self.sendMsgByQmsg({'type': 0, 'id': rcvAcc}, title, msg)
        if method == 4:
            return self.sendMsgByQmsg({'type': 1, 'id': rcvAcc}, title, msg)
        if method == 5:
            return self.sendMsgByQyWx(rcvAcc, title, msg)
        if method == 6:
            return self.sendMsgByServerChan(rcvAcc, title, msg)

        return '推送参数配置错误,已取消发送！'

    # 发送邮件消息
    def sendMsgByMailApi(self, mail, title, msg):
        if mail == '':
            return '邮箱为空,已取消邮箱API发送！'
        if self.option['mailApiUrl'] == '':
            return '邮件API为空,设置邮件API后才能发送邮件'
        # 以下部分需要根据不同接口自行修改
        params = {'recipient': mail, 'title': title, 'content': msg}
        res = requests.post(url=self.option['mailApiUrl'],
                            params=params).json()
        return "邮箱API%s" % (res['message'])

        # smtp本地邮件接口
    def sendMsgBySmtp(self, mail, title, msg):
        ret = "SMTP邮件发送成功"
        try:
            if mail == '':
                return '邮箱为空，已取消SMTP发送！'
            # 发信方的信息：发信邮箱，邮箱授权码
            from_addr = self.option['smtpOption']['userName']  # 发信方邮箱账号
            password = self.option['smtpOption']['passWord']  # 发信方邮箱密码
            if from_addr == '':
                return '发信邮箱地址为空,已取消SMTP发送！'
            if password == '':
                return '发信邮箱密码为空,已取消SMTP发送！'
            # 收信方邮箱
            to_addr = mail
            # 发信服务器
            smtp_server = self.option['smtpOption']['server']
            if smtp_server == '':
                return '发信邮箱服务器为空,已取消SMTP发送！'
            # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
            msg = MIMEText(msg, 'plain', 'utf-8')
            # 邮件头信息
            h = Header('今日校园', 'utf-8')
            # 允许自定义发信邮箱地址，需注意收信方安全策略问题
            h.append(from_addr, 'ascii')
            msg['From'] = h
            msg['To'] = Header(to_addr)
            msg['Subject'] = Header(title)
            # 开启发信服务，这里使用的是加密传输
            server = smtplib.SMTP_SSL(smtp_server, 465)
            # 登录发信邮箱
            server.login(from_addr, password)
            # 发送邮件
            server.sendmail(from_addr, to_addr, msg.as_string())
            # 关闭服务器
            server.quit()
        except Exception as e:  # 如果try中的语句没有执行，则会执行下面的ret=False
            ret = "SMTP邮件发送失败,%s" % (e)
        return ret

    def sendMsgByQmsg(self, qId, title, msg):
        if self.option['qmsgOption']['key'] == '':
            return 'QMSG的key为空,已取消发送消息！'
        if self.option['qmsgOption']['baseUrl'] == '':
            return 'QMSG的baseUrl为空,设置baseUrl后才能发送邮件'
        if qId['type'] == 1:
            url = self.option['qmsgOption'][
                'baseUrl'] + "group/" + self.option['qmsgOption']['key']
        else:
            url = self.option['qmsgOption']['baseUrl'] + "send/" + self.option[
                'qmsgOption']['key']
        params = {'msg': title + "\n" + msg, 'qq': qId['id']}
        res = requests.post(url, params=params).json()
        if res['success'] == True:
            return 'QMSG推送成功'
        else:
            return 'QMSG推送失败,' + res['reason']

    # 企业微信应用推送
    def sendMsgByQyWx(self, rcvAcc, title, message):
        wxConfig = self.option['qywxOption']

        def get_access_token(wxConfig):
            get_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
            response = requests.get(get_token_url, params=wxConfig).json()
            if response.get('access_token'):
                return response['access_token']
            else:
                print(response)
                return '获取access_token失败,已取消企业微信推送'

        if wxConfig['corpid'] and wxConfig['corpsecret']:
            try:
                access_token = get_access_token(wxConfig)
                if isinstance(access_token, str):
                    params = {
                        'touser': rcvAcc,
                        "agentid": wxConfig['agentid'],
                        "msgtype": "text",
                        'text': {
                            'content': f'{title}\n{message}'
                        }
                    }
                    url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
                    response = requests.post(url=url, json=params).json()
                    # print(response)
                    return '企业微信推送成功' if response[
                        'errmsg'] == 'ok' else response
                else:
                    print(access_token)
                    return access_token
            except Exception as e:
                return '企业微信推送失败,%s' % (e)
        else:
            return '企业微信应用配置错误,请检查qywxOption'

    # Server酱推送
    def sendMsgByServerChan(self, key, title, msg):
        if self.option['serverChanOption']['baseUrl'] == '':
            return 'Server酱的baseUrl为空,设置baseUrl后才能发送邮件'
        url = '{}{}.send'.format(
            self.option['serverChanOption']['baseUrl'], key)
        params = {'title': title, 'desp': msg}
        res = requests.post(url, params=params).json()
        if res['code'] == 0:
            return 'Server酱推送成功'
        else:
            return 'Server酱推送失败,' + res['message']

    # 其他通知方式待添加
