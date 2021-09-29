## 欢迎使用今日校园自动化

今日校园自动化是一个基于Python的爬虫项目，主要实现今日校园签到、信息收集、查寝等循环表单的自动化任务

该项目是由[ZimoLoveShuang/auto-submit](https://github.com/ZimoLoveShuang/auto-submit)仓库和[thriving123/f*kTodayStudy](https://github.com/thriving123/fuckTodayStudy)仓库基础上发展而来，请自行前往STAR，我们感谢原作者的努力与付出。

### 📃免责声明

本项目为Python学习交流的开源非营利项目，仅作为程序员之间相互学习交流之用，使用需严格遵守开源许可协议。严禁用于商业用途，禁止使用本项目进行任何盈利活动。对一切非法使用所产生的后果，我们概不负责。本项目对您如有困扰请联系我们删除。

### 📗使用方法

#### 🔑常规部署

 - 安装Python3.6+环境
 - 下载并解压项目代码包
 - 修改`config.yml`文件中的相关配置内容
 - 运行`pip install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple`安装项目依赖
 - 执行`Python index.py`即可运行项目

#### 🚀快速部署
 - Linux环境可以直接使用下方命令一键部署
	
	```
	curl -sSO https://gitee.com/icarlton/auto-cpdaily/raw/gh-pages/setup.sh && bash setup.sh
	```

#### 📅示例 腾讯云函数平台

 - 打开百度搜索[腾讯云函数](https://console.cloud.tencent.com/scf/index?rid=1)，注册认证后，进入控制台。
 - 点左边的函数服务，新建云函数，名称随意，运行环境选择`python3.6`，创建方式选择`自定义创建`
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
	curl -sSO https://gitee.com/icarlton/auto-cpdaily/raw/gh-pages/setup.sh && bash setup.sh
	```
	
 - 在编辑器左边的`src`目录下选择`config.yml`，配置你的用户签到信息，注意删除多余的示例并注意每行行首的缩进
 - 最后，点击下方的`部署`即可完成部署(部署完成后，你可以点击`测试`按钮测试签到任务)

#### 🔐进阶使用

- 如需推送提醒服务，请在`config.yml`顶部的`notifyOption`参数中进行配置
- 如需验证码识别需要先[开通腾讯OCR服务](https://console.cloud.tencent.com/ocr/overview)，然后[申请腾讯云API密钥](https://console.cloud.tencent.com/cam/capi)，最后将API密钥配置到路径`config.yml`里的`SecretId`以及`SecretKey`参数内

### 🔧常见问题

- 如果云函数报错`HTTP-418`请更换云函数其他地区节点
- 使用过程中报错`No module named 'XXXXX'`请重新安装依赖
- 请注意`config.yml`中每行参数的缩进位置，不然会产生错误

### 👨‍👨‍👦‍👦参与贡献

欢迎各位同学通过PR或者ISSUES的方式直接参与到项目中来，请注意反馈BUG需提供完整日志！

### 📜许可证

本项目的源代码在MPL2.0协议下发布，同时附加以下条目：
* **非商业性使用** — 不得将此项目及其衍生的项目的源代码和二进制产品用于任何商业和盈利用途
