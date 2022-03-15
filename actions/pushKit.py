import requests
import apprise


# 消息通知聚合类
class pushKit:
    # 初始化类
    def __init__(self, option):
        self.option = option
        self.type = option['method']

    def sendMsg(self, title, msg, user=''):
        if 'notifyOption' not in user:
            return '该用户未配置推送,已取消发送！'
        if 'rcvOption' not in user['notifyOption']:
            return '该用户未配置推送,已取消发送！'
        if user['notifyOption']['rcvOption'] == "":
            return '该用户未配置推送,已取消发送！'

        userOption = user['notifyOption']
        # 获取接收账号
        rcvOption = userOption['rcvOption']
        # 获取全局推送模式
        method = self.type
        # 获取用户指定的推送模式
        if 'method' in userOption:
            method = userOption['method']

        # 判断推送类型
        if method == 0:
            return '消息推送服务未启用'
        if method == 1:
            return self.sendMsgByMailApi(rcvOption, title, msg)
        if method == 2:
            return self.sendMsgByOther(rcvOption, title, msg)

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

    def sendMsgByOther(self, rcvOption, title, msg):
        pusher = apprise.Apprise()
        pusher.add(rcvOption)
        res = pusher.notify(
            body=msg,
            title=title,
        )

        if res == True:
            return "APPRISE推送消息成功"
        else:
            return "APPRISE推送消息失败"
