## 欢迎使用今日校园自动化

今日校园自动化是一个基于Python的爬虫项目，主要实现今日校园签到、信息收集、查寝等循环表单的自动化任务

该项目是由[ZimoLoveShuang/auto-submit](https://github.com/ZimoLoveShuang/auto-submit)仓库基础上发展而来，请自行前往STAR，我们感谢原作者的努力与付出。该项目现在由[Thriving123](https://github.com/thriving123)与[Carlton](https://github.com/carltonhere)维护。

### 📃免责声明

AutoCpdaily为Python学习交流的开源非营利项目，仅作为程序员之间相互学习交流之用，使用需严格遵守开源许可协议。严禁用于商业用途，禁止使用AutoCpdaily进行任何盈利活动。对一切非法使用所产生的后果，我们概不负责。本项目对您如有困扰请联系我们删除。

### 📗使用方法

#### 🔑快速使用

 - 下载并解压项目代码包
 - 修改`Config.yml`文件中的相关配置内容
 - 在根目录运行`pip install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple`安装项目依赖
 - 执行`Python index.py`即可运行项目

#### 📅示例 腾讯云函数平台

 - 下载项目代码包，无需解压
 - 打开百度搜索[腾讯云函数](https://console.cloud.tencent.com/scf/index?rid=1)，注册认证后，进入控制台。
 - 点左边的函数服务，新建云函数，名称随意，运行环境选择`python3.6`，创建方式选择`自定义创建`，提交方式选择`本地上传zip包`并上传下载好的项目代码包
 - 在`高级配置`中配置`执行超时时间`60秒，在`触发器配置`中选择自定义创建，`触发周期`选择自定义触发，配置cron表达式，下方举例三个常用配置
 - 点击完成，不要关闭页面等待创建完成后，选择立即跳转
 - 点击函数代码选项卡，在左边的`src`目录下选择`config.yml`，配置你的用户签到信息，注意删除多余的示例并注意每行行首的缩进
 - 在编辑器上方的菜单栏中，选择`终端`>`新终端`，在下方弹出的终端里输入`pip3 install -r src/requirements.txt -t src -i https://mirrors.aliyun.com/pypi/simple`并回车安装项目依赖
 - 等待依赖安装完毕，点击下方的`部署`即可完成部署

```
如需每日上午0点执行可使用该表达式
0 0 0 * * * *
如需每日上午8点30分执行可使用该表达式
0 30 8 * * * *
如需每日中午12点执行可使用该表达式
0 0 12 * * * *
```

#### 🔐进阶使用

- 如需推送提醒服务，请在`Config.yml`顶部的`notifyOption`参数中进行配置
- 如需验证码识别需要先[开通腾讯OCR服务](https://console.cloud.tencent.com/ocr/overview)，然后[申请腾讯云API密钥](https://console.cloud.tencent.com/cam/capi)，最后将API密钥配置到路径`Config.yml`里的`SecretId`以及`SecretKey`参数内

### 🔧常见问题

- 如果云函数报错`HTTP-418`请更换云函数其他地区节点
- 使用过程中报错`No module named 'XXXXX'`请重新安装依赖
- 请注意`Config.yml`中每行参数的缩进位置，不然会产生错误

### 👨‍👨‍👦‍👦参与贡献

欢迎各位同学通过PR或者ISSUES的方式直接参与到项目中来，请注意反馈BUG需提供完整日志！
