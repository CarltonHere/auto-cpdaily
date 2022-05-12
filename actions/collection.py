import json
from actions.utils import Utils
from actions.wiseLoginService import wiseLoginService


class Collection:
    # 初始化信息收集类
    def __init__(self, wiseLoginService: wiseLoginService, userInfo):
        self.session = wiseLoginService.session
        self.host = wiseLoginService.campus_host
        self.userInfo = userInfo
        self.form = None
        self.collectWid = None
        self.formWid = None
        self.schoolTaskWid = None
        self.instanceWid = None
        self.apis = Utils.getApis(userInfo['type'])

    # 查询表单
    def queryForm(self):
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        queryUrl = self.host + self.apis[0]
        params = {"pageSize": 20, "pageNumber": 1}
        res = self.session.post(queryUrl,
                                data=json.dumps(params),
                                headers=headers,
                                verify=False).json()
        if len(res['datas']['rows']) < 1:
            raise Exception('当前暂时没有未完成的信息收集哦！')
        for item in res['datas']['rows']:
            if item['isHandled'] == 0:
                self.collectWid = item['wid']
                self.formWid = item['formWid']
                self.instanceWid = item['instanceWid']
            if "formTitle" in self.userInfo:
                if (item["subject"]).find(self.userInfo["formTitle"]) > -1:
                    self.collectWid = item['wid']
                    self.formWid = item['formWid']
                    self.instanceWid = item['instanceWid']
        if (self.formWid == None):
            raise Exception('当前暂时没有未完成的信息收集哦！')
        detailUrl = self.host + self.apis[1]
        res = self.session.post(detailUrl,
                                headers=headers,
                                data=json.dumps({
                                    "collectorWid": self.collectWid,
                                    "instanceWid": self.instanceWid
                                }),
                                verify=False).json()
        self.schoolTaskWid = res['datas']['collector']['schoolTaskWid']
        getFormUrl = self.host + self.apis[2]
        params = {
            "pageSize": 100,
            "pageNumber": 1,
            "formWid": self.formWid,
            "collectorWid": self.collectWid,
            "instanceWid": self.instanceWid
        }
        res = self.session.post(getFormUrl,
                                headers=headers,
                                data=json.dumps(params),
                                verify=False).json()
        self.form = res['datas']['rows']

    # 填写表单
    def fillForm(self):
        index = 0
        onlyRequired = self.userInfo[
            'onlyRequired'] if 'onlyRequired' in self.userInfo else 1
        for formItem in self.form[:]:
            if onlyRequired == 1:
                if not formItem['isRequired']:
                    # 移除非必填选项
                    self.form.remove(formItem)
                    continue
            try:
                userForm = self.userInfo['forms'][index]['form']
            except:
                raise Exception('请检查forms配置是否正确！')
            # 判断用户是否需要检查标题
            if self.userInfo['checkTitle'] == 1:
                # 如果检查到标题不相等
                if formItem['title'] != userForm['title']:
                    raise Exception(
                        f'\r\n第{index + 1}个配置项的标题不正确\r\n您的标题为：[{userForm["title"]}]\r\n系统的标题为：[{formItem["title"]}]'
                    )
            # 忽略用户指定题目
            if 'ignore' in userForm and userForm['ignore']:
                formItem['value'] = None
                # 设置显示为false
                formItem['show'] = False
                # 清空所有的选项
                if 'fieldItems' in formItem:
                    formItem['fieldItems'].clear()
                index += 1
                continue
            formType = formItem['fieldType']
            if 'forceType' in userForm and userForm['forceType']:
                formType = userForm['forceType']
            # 文本选项直接赋值
            if formType in ('1', '5', '6', '7', '11', '12'):
                formItem['value'] = userForm['value']
            # 单选框填充
            elif formType == '2':
                # 单选需要移除多余的选项
                fieldItems = formItem['fieldItems']
                for fieldItem in fieldItems[:]:
                    if fieldItem['content'] == userForm['value']:
                        formItem['value'] = fieldItem['itemWid']
                        if fieldItem['isOtherItems'] and fieldItem[
                                'otherItemType'] == '1':
                            if 'extra' not in userForm:
                                raise Exception(
                                    f'\r\n第{index + 1}个配置项的选项不正确,该选项需要extra字段')
                            fieldItem['contentExtend'] = userForm['extra']
                    else:
                        fieldItems.remove(fieldItem)
                if len(fieldItems) != 1:
                    raise Exception(f'\r\n第{index + 1}个配置项的选项不正确,该选项为必填单选')
            # 多选填充
            elif formType == '3':
                fieldItems = formItem['fieldItems']
                userItems = userForm['value'].split('|')
                tempValue = []
                for fieldItem in fieldItems[:]:
                    if fieldItem['content'] in userItems:
                        tempValue.append(fieldItem['itemWid'])
                        if fieldItem['isOtherItems'] and fieldItem[
                                'otherItemType'] == '1':
                            if 'extra' not in userForm:
                                raise Exception(
                                    f'\r\n第{index + 1}个配置项的选项不正确,该选项需要extra字段')
                            fieldItem['contentExtend'] = userForm['extra']
                    else:
                        fieldItems.remove(fieldItem)
                if len(fieldItems) == 0:
                    raise Exception(f'\r\n第{index + 1}个配置项的选项不正确,该选项为必填多选')
                formItem['value'] = ','.join(tempValue)
            elif formType in ('4', '16'):
                dirList = list(userForm['value'])
                # 检查列表长度
                dirListLen = len(dirList)
                if dirListLen > 10 or dirListLen == 0:
                    raise Exception(
                        f'\r\n第{index + 1}个配置项配置的图片数量({dirListLen})不符合要求')
                # 将列表中的每一项都加入到value中
                imgUrlList = []
                for i, pic in enumerate(dirList, 1):
                    fileName = Utils.uploadPicture(self, self.apis[4], pic)
                    imgUrl = Utils.getPictureUrl(self, self.apis[5], fileName)
                    imgUrlList.append(imgUrl)
                formItem['value'] = ",".join(imgUrlList)
            else:
                raise Exception(
                    f'\r\n第{index + 1}个配置项的类型{formItem.fieldType}未适配')
            index += 1

    # 提交表单
    def submitForm(self):
        self.submitData = {
            "formWid": self.formWid,
            "address": self.userInfo['address'],
            "collectWid": self.collectWid,
            "instanceWid": self.instanceWid,
            "schoolTaskWid": self.schoolTaskWid,
            "form": self.form,
            "uaIsCpadaily": True,
            "latitude": self.userInfo['lat'],
            'longitude': self.userInfo['lon']
        }
        self.submitApi = self.apis[3]
        res = Utils.submitFormData(self).json()
        return res['message']
