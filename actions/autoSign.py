import json
from actions.utils import Utils
from actions.wiseLoginService import wiseLoginService


class AutoSign:
    # 初始化签到类
    def __init__(self, wiseLoginService: wiseLoginService, userInfo):
        self.session = wiseLoginService.session
        self.host = wiseLoginService.campus_host
        self.userInfo = userInfo
        self.taskInfo = None
        self.task = None
        self.form = {}
        self.fileName = None
        self.apis = Utils.getApis(userInfo['type'])

    # 获取未签到的任务
    def getUnSignTask(self):
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        # 第一次请求接口获取cookies（MOD_AUTH_CAS）
        url = self.host + self.apis[0]
        self.session.post(url,
                          headers=headers,
                          data=json.dumps({}),
                          verify=False)
        # 第二次请求接口，真正的拿到具体任务
        res = self.session.post(url,
                                headers=headers,
                                data=json.dumps({}),
                                verify=False).json()
        if len(res['datas']['unSignedTasks']) < 1:
            if len(res['datas']['leaveTasks']) < 1:
                raise Exception('当前暂时没有未签到的任务哦！')
            latestTasks = res['datas']['leaveTasks']
        else:
            latestTasks = res['datas']['unSignedTasks']
        latestTask = latestTasks[0]
        if "formTitle" in self.userInfo:
            for formItem in latestTasks:
                if (formItem['taskName']).find(self.userInfo["formTitle"]) > -1:
                    latestTask = formItem
        self.taskInfo = {
            'signInstanceWid': latestTask['signInstanceWid'],
            'signWid': latestTask['signWid']
        }

    # 获取具体的签到任务详情
    def getDetailTask(self):
        url = self.host + self.apis[1]
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        res = self.session.post(url,
                                headers=headers,
                                data=json.dumps(self.taskInfo),
                                verify=False).json()
        self.task = res['datas']

    # 填充表单
    def fillForm(self):
        # 判断签到是否需要照片
        if self.task['isPhoto'] == 1:
            fileName = Utils.uploadPicture(
                self, self.apis[3], self.userInfo['photo'])
            self.form['signPhotoUrl'] = Utils.getPictureUrl(
                self, self.apis[4], fileName)
        else:
            self.form['signPhotoUrl'] = ''
        if 'isNeedExtra' in self.task:
            self.form['isNeedExtra'] = self.task['isNeedExtra']
        else:
            self.task['isNeedExtra'] = 0
        if self.task['isNeedExtra'] == 1:
            extraFields = self.task['extraField']
            userItems = self.userInfo['forms']
            extraFieldItemValues = []
            for i in range(len(extraFields)):
                userItem = userItems[i]['form']
                extraField = extraFields[i]
                if self.userInfo['checkTitle'] == 1:
                    if userItem['title'] != extraField['title']:
                        raise Exception(
                            f'\r\n第{i + 1}个配置出错了\r\n您的标题为：[{userItem["title"]}]\r\n系统的标题为：[{extraField["title"]}]'
                        )
                extraFieldItems = extraField['extraFieldItems']
                flag = False
                data = 'NULL'
                for extraFieldItem in extraFieldItems:
                    if extraFieldItem['isSelected']:
                        data = extraFieldItem['content']
                    # print(extraFieldItem)
                    if extraFieldItem['content'] == userItem['value']:
                        if extraFieldItem['isOtherItems'] == 1:
                            if 'extra' in userItem:
                                flag = True
                                extraFieldItemValue = {
                                    'extraFieldItemValue': userItem['extra'],
                                    'extraFieldItemWid': extraFieldItem['wid']
                                }
                                extraFieldItemValues.append(
                                    extraFieldItemValue)
                            else:
                                raise Exception(
                                    f'\r\n第{ i + 1 }个配置出错了\r\n表单未找到你设置的值：[{userItem["value"]}],\r\n该选项需要extra字段'
                                )
                        else:
                            flag = True
                            extraFieldItemValue = {
                                'extraFieldItemValue': userItem['value'],
                                'extraFieldItemWid': extraFieldItem['wid']
                            }
                            extraFieldItemValues.append(extraFieldItemValue)
                if not flag:
                    raise Exception(
                        f'\r\n第{ i + 1 }个配置出错了\r\n表单未找到你设置的值：[{userItem["value"]}],\r\n你上次系统选的值为：[{data}]'
                    )
            self.form['extraFieldItems'] = extraFieldItemValues
        self.form['signInstanceWid'] = self.task['signInstanceWid']
        self.form['longitude'] = self.userInfo['lon']
        self.form['latitude'] = self.userInfo['lat']
        self.form['isMalposition'] = self.task['isMalposition']
        self.form['abnormalReason'] = self.userInfo[
            'abnormalReason'] if 'abnormalReason' in self.userInfo else ''
        self.form['position'] = self.userInfo['address']
        self.form['uaIsCpadaily'] = True
        self.form['signVersion'] = '1.0.0'

    # 提交签到信息
    def submitForm(self):
        # print(json.dumps(self.form))
        self.submitData = self.form
        self.submitApi = self.apis[2]
        res = Utils.submitFormData(self).json()
        return res['message']
