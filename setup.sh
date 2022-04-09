#!/bin/bash

Get_Pack_Manager(){
	if [ -f "/usr/bin/yum" ] && [ -d "/etc/yum.repos.d" ]; then
		PM="yum"
	elif [ -f "/usr/bin/apt-get" ] && [ -f "/usr/bin/dpkg" ]; then
		PM="apt-get"		
	fi
}

Set_Auto_Cpdaily(){
	echo "开始下载项目代码"
	wget --no-check-certificate -O code.zip http://download.fastgit.org/carltonhere/auto-cpdaily/archive/main.zip
	echo "开始解压项目代码"
	unzip -o code.zip
	echo "开始初始化项目依赖"
	pip3 install -r auto-cpdaily-main/requirements.txt -t auto-cpdaily-main/ -i https://mirrors.aliyun.com/pypi/simple
	cp -r auto-cpdaily-main/* $local_file
	rm -rf code.zip
	rm -rf auto-cpdaily-main/
}

Install_Env_Pack(){
	echo '开始部署系统基础环境'
	if [ "${PM}" = "yum" ]; then
		echo '暂不支持该发行版'
		exit 1
	elif [ "${PM}" = "apt-get" ]; then
		apt-get update -y
		apt-get install wget unzip python3 python3-pip -y
	fi
}
echo "================================================"
echo "            欢迎使用今日校园自动化"
echo "================================================"
echo "请输入当前脚本运行环境的序号"
select var in "腾讯云函数" "阿里云函数" "其他Linux环境";do
break
done

if [ "$var" = "腾讯云函数" ];then
local_file="./src/"
if [ ! -d $local_file ]; then
        mkdir $local_file
fi
echo '即将开始部署腾讯函数环境'
elif [ "$var" = "阿里云函数" ];then
local_file="."
echo '即将开始部署阿里云函数环境'
else
local_file="."
echo '即将开始部署标准Linux环境'
Get_Pack_Manager
Install_Env_Pack
fi

Set_Auto_Cpdaily

echo "================================================"
echo "项目初始化完成，请自行修改config.yml内的用户参数"
echo "服务器环境请输入'python3 index.py'运行项目"
echo "云函数环境不要忘记点击部署按钮上传配置！！！"
echo "云函数环境不要忘记点击部署按钮上传配置！！！"
echo "云函数环境不要忘记点击部署按钮上传配置！！！"
echo "================================================"

rm -rf setup.sh
