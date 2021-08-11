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
        if('notifyOption' in user):
            userOption = user['notifyOption']
        else:
            return '该用户未配置推送，已取消发送！'
        method = self.type
        if('method' in userOption):
            method = userOption['method']
        # 判断推送类型
        if 'email' in userOption:
            if method == 1:
                return self.sendMsgByMailApi(userOption['email'], title, msg)
            elif method == 2:
                return self.sendMsgBySmtp(userOption['email'], title, msg)
        if 'qId' in userOption:
            if method == 3:
                return self.sendMsgByQmsg(userOption['qId'], title, msg)
        if method == 0:
            return '消息推送服务未启用'
        return '推送参数配置错误，已取消发送！'

    # 发送邮件消息
    def sendMsgByMailApi(self, mail, title, msg):
        if mail == '':
            return '邮箱为空，已取消发送邮件！'
        if self.option['apiUrl'] == '':
            return '邮件API为空，设置邮件API后才能发送邮件'
        params = {'to': mail, 'title': title, 'content': msg}
        res = requests.post(url=self.option['apiUrl'], params=params).json()
        return res['msg']

        # smtp本地邮件接口
    def sendMsgBySmtp(self, mail, title, msg):
        ret = "邮件发送成功"
        try:
            if mail == '':
                return '邮箱为空，已取消发送邮件！'
            # 发信方的信息：发信邮箱，邮箱授权码
            from_addr = self.option['smtpOption']['userName']  # 发信方邮箱账号
            password = self.option['smtpOption']['passWord']  # 发信方邮箱密码
            if from_addr == '':
                return '发信邮箱地址为空，已取消发送邮件！'
            if password == '':
                return '发信邮箱密码为空，已取消发送邮件！'
            # 收信方邮箱
            to_addr = mail
            # 发信服务器
            smtp_server = self.option['smtpOption']['server']
            if smtp_server == '':
                return '发信邮箱服务器为空，已取消发送邮件！'
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
        except Exception:  #如果try中的语句没有执行，则会执行下面的ret=False
            ret = "邮件发送失败"
        return ret

    def sendMsgByQmsg(self, qId, title, msg):
        if self.option['qmsgOption']['key'] == '':
            return 'qmsg的key为空，已取消发送消息！'
        if self.option['qmsgOption']['baseUrl'] == '':
            return 'qmsg的baseUrl为空，设置baseUrl后才能发送邮件'
        if qId['type'] == 1:
            url = self.option['qmsgOption'][
                'baseUrl'] + "group/" + self.option['qmsgOption']['key']
        else:
            url = self.option['qmsgOption']['baseUrl'] + "send/" + self.option[
                'qmsgOption']['key']
        params = {'msg': title + "\n" + msg, 'qq': qId['id']}
        res = requests.post(url, params=params).json()
        if (res['success'] == True):
            return 'qmsg推送成功'
        else:
            return 'qmsg推送失败,' + res['reason']

    # 其他通知方式待添加
