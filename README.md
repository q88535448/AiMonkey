# AiMonkey
## 简介
AI Monkey项目是封装了目前火热的测试工具[Maxim](https://github.com/zhangzhao4444/Maxim)。主要修改点有如下几个
* 解决了该工具偶尔进入页面长时间无法返回的问题。提高遍历效率
* 封装了工具启动命令，简化启动方式
* 封装了部分产品的登录方法（仅支持google+登录，请先在手机配置好）
* 支持多设备并行，设备id空格分割

## 环境要求
* mac linux windows
* python2.7
* adb

## 快速开始
* git clone https://github.com/q88535448/AiMonkey.git
* cd AiMonkey
* python setup.py install

## 启动命令
不提供安装路径（确保已安装好应用并完成登录等操作)，特别注意：在安装apk的时候务必加上-g命令默认授权，示例 adb -s xxxx install -g xxxxx.apk
* python run.py run_monkey -s xxxxx(设备id) -p com.xxxx.xxxx(包名) --runningminutes 10（执行时间）

提供apk路径
* python run.py run_monkey -s xxxxx --apk apkPath(apk绝对路径) --runningminutes 10

多终端同时测试
* python run.py run_monkey -s xxxxx&xxxx --apk apkPath(apk绝对路径) --runningminutes 10

查看全部命令
* python2 run.py run_monkey --help
* --throttle 默认执行间隔700毫秒，太快程序扛不住，可自行设置

## 遍历模式
* 模式 DFS：--uiautomatordfs 深度遍历模式，按照层级点击，会重复点击
* 模式 Mix：--uiautomatormix 直接使用底层accessibiltyserver获取界面接口 解析各控件，随机选取一个控件执行touch操作。同时与原monkey 其他操作按比例混合使用默认accessibilityserver action占比70%，其余各action分剩余的30%，accessibilityserver action占比可配置 --pct-uiautomatormix n
* 从测试效果看，Mix模式会优于DFS模式，经验之谈。

## 执行结果
* 如果出现崩溃或anr程序会自动把日志抓出来保存到根目录logs/crash-dump.log，没有这个文件说明没有发生crash或anr
* logcat.log是标准的androidlog，monkeyout.log是工具执行过程中产生的日志加monkey本身日志。



