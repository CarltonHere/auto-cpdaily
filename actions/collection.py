import base64
import json
import re
import uuid
from pyDes import PAD_PKCS5, des, CBC
from login.Utils import Utils
from login.wiseLoginService import wiseLoginService


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

    # 查询表单
    def queryForm(self):
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        queryUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'
        params = {'pageSize': 20, "pageNumber": 1}
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
        if (self.formWid == None):
            raise Exception('当前暂时没有未完成的信息收集哦！')
        detailUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/detailCollector'
        res = self.session.post(detailUrl,
                                headers=headers,
                                data=json.dumps(
                                    {'collectorWid': self.collectWid}),
                                verify=False).json()
        self.schoolTaskWid = res['datas']['collector']['schoolTaskWid']
        getFormUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/getFormFields'
        params = {
            "pageSize": 100,
            "pageNumber": 1,
            "formWid": self.formWid,
            "collectorWid": self.collectWid
        }
        res = self.session.post(getFormUrl,
                                headers=headers,
                                data=json.dumps(params),
                                verify=False).json()
        self.form = res['datas']['rows']

    # 填写表单
    def fillForm(self):
        index = 0
        onlyRequired = self.userInfo['onlyRequired'] if 'onlyRequired' in self.userInfo else 1
        for formItem in self.form[:]:
            if onlyRequired == 1:
                if not formItem['isRequired']:
                    # 移除非必填选项
                    self.form.remove(formItem)
                    continue
            userForm = self.userInfo['forms'][index]['form']
            # 判断用户是否需要检查标题
            if self.userInfo['checkTitle'] == 1:
                # 如果检查到标题不相等
                if formItem['title'] != userForm['title']:
                    raise Exception(
                        f'\r\n第{index + 1}个配置项的标题不正确\r\n您的标题为：[{userForm["title"]}]\r\n系统的标题为：[{formItem["title"]}]'
                    )
            # 文本选项直接赋值
            if formItem['fieldType'] in ['1', '5', '6', '7']:
                formItem['value'] = userForm['value']
            # 单选框填充
            elif formItem['fieldType'] == '2':
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
            elif formItem['fieldType'] == '3':
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
            elif formItem['fieldType'] == '4':
                Utils.uploadPicture(self, 'collector', userForm['value'])
                formItem['value'] = Utils.getPictureUrl(self, 'collector')
            else:
                raise Exception(f'\r\n第{index + 1}个配置项的类型未适配')
            index += 1

    # 提交表单
    def submitForm(self):
        extension = {
            "model": "OPPO R11 Plus",
            "appVersion": "8.2.14",
            "systemVersion": "9.1.0",
            "userId": self.userInfo['username'],
            "systemName": "android",
            "lon": self.userInfo['lon'],
            "lat": self.userInfo['lat'],
            "deviceId": str(uuid.uuid1())
        }

        headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Cpdaily-Extension': self.DESEncrypt(json.dumps(extension)),
            'Content-Type': 'application/json; charset=utf-8',
            # 请注意这个应该和配置文件中的host保持一致
            'Host': re.findall('//(.*?)/', self.host)[0],
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        params = {
            "formWid": self.formWid,
            "address": self.userInfo['address'],
            "collectWid": self.collectWid,
            "schoolTaskWid": self.schoolTaskWid,
            "form": self.form,
            "uaIsCpadaily": True,
            "latitude": self.userInfo['lat'],
            'longitude': self.userInfo['lon']
        }
        submitUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/submitForm'
        data = self.session.post(submitUrl,
                                 headers=headers,
                                 data=json.dumps(params),
                                 verify=False).json()
        return data['message']

    # DES加密
    def DESEncrypt(self, content):
        key = 'b3L26XNL'
        iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        encrypt_str = k.encrypt(content)
        return base64.b64encode(encrypt_str).decode()
