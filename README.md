## 欢迎使用今日校园自动化

今日校园自动化是一个基于Python的爬虫项目，能够实现今日校园签到、信息收集、查寝等循环表单的自动化工作

### 📃免责声明

本项目为Python学习交流的开源非营利项目，仅作为程序员之间相互学习交流之用，使用需严格遵守开源许可协议。严禁用于商业用途，禁止使用本项目进行任何盈利活动。对一切非法使用所产生的后果，我们概不负责。本项目对您如有困扰请联系我们删除。

### 📗使用方法

#### 🔑常规部署

 - 安装Python3.7+环境
 - 下载并解压项目代码包
 - 修改`config.yml`文件中的相关配置内容
 - 运行`pip install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple`安装项目依赖
 - 执行`Python index.py`即可运行项目

#### 🚀快速部署
 - Linux环境可以直接使用下方命令一键部署
	
	```
	curl -sSO https://cdn.staticaly.com/gh/CarltonHere/auto-cpdaily/gh-pages/setup.sh && bash setup.sh
	```

#### 📅示例 腾讯云函数平台

 - 打开百度搜索[腾讯云函数](https://console.cloud.tencent.com/scf/index?rid=1)，注册认证后，进入控制台。
 - 点左边的函数服务，新建云函数，名称随意，运行环境选择`python3.7`，创建方式选择`自定义创建`
 - 在`高级配置`中配置`执行超时时间`60秒，在`触发器配置`中选择自定义创建，`触发周期`选择自定义触发，配置cron表达式
	
	```
	如需每日上午0点执行可使用该表达式
	0 0 0 * * * *
	如需每日上午8点30分执行可使用该表达式
	0 30 8 * * * *
	如需每日中午12点执行可使用该表达式
	0 0 12 * * * *
	```
	
 - 点击完成，不要关闭页面等待创建完成后，选择立即跳转
 - 点击`函数代码`选项卡，等待编辑器初始化完成
 - 在编辑器上方的菜单栏中，选择`终端`>`新终端`，将下方命令粘贴到弹出的终端中并回车，等待初始化环境完成，可能需要较长时间，请耐心等待(如长时间没反应可以按下`CTRL`+`C`键强制终止，然后再次尝试)
	
	```
	curl -sSO https://raw.fastgit.org/CarltonHere/auto-cpdaily/gh-pages/setup.sh && bash setup.sh
	```
	
 - 在编辑器左边的`src`目录下选择`config.yml`，配置你的用户签到信息，注意删除多余的示例并注意每行行首的缩进
 - 最后，点击下方的`部署`即可完成部署(部署完成后，你可以点击`测试`按钮测试签到任务)

#### 🔐进阶使用

 - 如需推送提醒服务，请在`config.yml`顶部的`notifyOption`中配置模式，然后在每个用户的`rcvOption`中配置APPRISE参数即可，推荐使用APPRISE推送模式，该模式支持邮箱、钉钉、ServerChan等推送渠道，更多信息请访问[APPRISE项目维基](https://github.com/caronc/apprise/wiki)。篇幅有限，只演示配置邮箱推送：
	
	```
	users:
    - user:
		notifyOption: 
			# 首先配置推送模式为2，即APPRISE推送模式
			method: 2
			# 然后配置APPRISE参数，填写您的邮箱账号和密码
			# 此处需要注意，qq、163等邮箱平台需要使用smtp授权码代替密码
			# 末尾的'?to=收信人邮箱'如果省略则默认发给自己
			# 账号是邮箱地址@符号前的部分，比如admin@163.com的账号为admin
			rcvOption: 'mailto://smtp账号:smtp密码@163.com/?to=收信人邮箱'
	```
	
- 如需忽略必填题目，请在`form`下新增`ignore: True`字段，请您注意题目要求留空的，请将`form`下的`value`字段按照`value: ""`这种方式设置，`ignore: True`主要用于隐藏题目，错误的隐藏必填项会导致签到异常！
- 如需验证码识别需要先[开通腾讯OCR服务](https://console.cloud.tencent.com/ocr/overview)，然后[申请腾讯云API密钥](https://console.cloud.tencent.com/cam/capi)，最后将API密钥配置到路径`config.yml`里的`SecretId`以及`SecretKey`参数内
- 如需指定执行特定的任务表单，请在`user`下新增`formTitle`字段，并配置您要执行的任务表单名称

### 🔧常见问题

 - 如果云函数报错`HTTP-418`请更换云函数其他地区节点
 - 使用过程中报错`No module named 'XXXXX'`请重新安装依赖
 - 请注意`config.yml`中每行参数的缩进位置，不然会产生错误

### 👨‍👨‍👦‍👦参与贡献

欢迎各位同学通过PR或者ISSUES的方式直接参与到项目中来，请注意反馈BUG需提供完整日志！

### ❤️同类作品

感谢同类项目的存在，让社区能够相互学习和进步，请自行前往Star，我们感谢他们所做的贡献！

 - [ZimoLoveShuang/auto-submit](https://github.com/ZimoLoveShuang/auto-submit)
 - [thriving123/f*kTodayStudy](https://github.com/thriving123/fuckTodayStudy)
 - [IceTiki/ruoli-sign-optimization](https://github.com/IceTiki/ruoli-sign-optimization)
 - [windowsair/fzu-cpDailySign](https://github.com/windowsair/fzu-cpDailySign)
 - [ceajs/cea](https://github.com/ceajs/cea)

### 📜许可证

本项目的源代码在MPL2.0协议下发布，同时附加以下条目：
* **非商业性使用** — 不得将此项目及其衍生的项目的源代码和二进制产品用于任何商业和盈利用途
