import json
from actions.Utils import Utils
from actions.wiseLoginService import wiseLoginService


class sleepCheck:
    # 初始化信息收集类
    def __init__(self, wiseLoginService: wiseLoginService, userInfo):
        self.session = wiseLoginService.session
        self.host = wiseLoginService.campus_host
        self.userInfo = userInfo
        self.taskInfo = None
        self.form = {}

    # 获取未签到任务
    def getUnSignedTasks(self):
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        # 第一次请求接口获取cookies（MOD_AUTH_CAS）
        url = f'{self.host}wec-counselor-attendance-apps/student/attendance/getStuAttendacesInOneDay'
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
            raise Exception('当前暂时没有未签到的任务哦！')
        # 获取最后的一个任务
        latestTask = res['datas']['unSignedTasks'][0]
        self.taskInfo = {
            'signInstanceWid': latestTask['signInstanceWid'],
            'signWid': latestTask['signWid']
        }

    # 获取具体的签到任务详情
    def getDetailTask(self):
        url = f'{self.host}wec-counselor-attendance-apps/student/attendance/detailSignInstance'
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
            Utils.uploadPicture(self, 'sign', self.userInfo['photo'])
            self.form['signPhotoUrl'] = Utils.getPictureUrl(self, 'sign')
        else:
            self.form['signPhotoUrl'] = ''
        self.form['signInstanceWid'] = self.taskInfo['signInstanceWid']
        self.form['longitude'] = self.userInfo['lon']
        self.form['latitude'] = self.userInfo['lat']
        self.form['isMalposition'] = self.task['isMalposition']
        self.form['abnormalReason'] = self.userInfo['abnormalReason']
        self.form['position'] = self.userInfo['address']
        self.form['qrUuid'] = ''
        self.form['uaIsCpadaily'] = True

    # 提交签到信息
    def submitForm(self):
        self.submitData = self.form
        self.submitApi = 'wec-counselor-sign-apps/stu/sign/submitSign'
        res = Utils.submitFormData(self).json()
        return res['message']
