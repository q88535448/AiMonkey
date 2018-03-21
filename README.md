# AiMonkey
## 简介
AI Monkey项目是封装了目前火热的测试工具[Maxim](https://github.com/zhangzhao4444/Maxim)。主要修改点有如下几个
* 解决了该工具偶尔进入页面长时间无法返回的问题。提高便利效率
* 封装了工具启动命令，简化启动方式
* 封装了部分产品的登录方法（仅支持google+登录，请先在手机配置好）

## 环境要求
* mac linux windows
* python2.7

## 快速开始
* git clone https://github.com/q88535448/AiMonkey.git
* cd AiMonkey
* python setup.py install

## 启动命令
不提供安装路径（确保已安装好应用并完成登录）
* python run.py run_monkey -s xxxxx(设备id) -p com.xxxx.xxxx(包名) --runningminutes 10（执行时间）

提供apk路径
* python run.py run_monkey -s xxxxx --apk apkPath(apk绝对路径) --runningminutes 10

查看全部命令
* python2 run.py run_monkey --help

