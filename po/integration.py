# -*- coding: utf-8 -*-
import threading

from po import getback_strategy
import lib.Utils as U
import subprocess
import public.Analyzelog as l
import lib.package as pkg
from public.InstallApp import InstallApp
from public.login import LoginApp
from lib.adbUtils import ADB
from lib.adbUtils import system

__author__ = 'xiaqing'

"""
@author:xiaqing
@time: 16/11/15 下午1:44
"""


class RunMonkey(object):
    def __init__(self, serial, pkgname, apk_path, mode, runningminutes, throttle, pctuiautomatormix):
        self.serial = serial
        self.apk_path = apk_path
        self.mode = mode
        self.adb = ADB(serial)
        self.runningminutes = runningminutes
        self.throttle = throttle
        self.pctuiautomatormix = pctuiautomatormix
        self.process = None
        if apk_path:
            self.package = pkg.Package(self.apk_path)
            self.pkgname = self.package.name
        else:
            self.pkgname = pkgname
            self.package = None

        self.dl = l.DeviceLog(serial, self.pkgname)


    def __del__(self):
        # windows adb不会释放logc.log需要强制释放一下
        if system is "Windows":
            U.cmd("taskkill /im adb.exe /f")

    def __start_back_strategy(self):
        U.Logging.info("start the thread of getback_strategy")
        self.man_talk_event = threading.Event()
        test_run = getback_strategy.r(self.serial, int(self.runningminutes), self.throttle, self.package, self.man_talk_event)
        test_run.start()

    def __start_new_monkey(self):
        U.Logging.info("run the AI monkey cmd")
        if self.mode == '--uiautomatormix':
            cmd = 'adb -s %s shell "CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar exec app_process /system/bin tv.panda.test.monkey.Monkey ' \
                  '-p %s --%s --running-minutes %s --pct-uiautomatormix %s --ignore-crashes --ignore-timeouts --throttle %s -v -v -v -v > /sdcard/monkeyout.txt 2>/sdcard/monkeyerr.txt" ' % (
                      self.serial, self.pkgname, self.mode, self.runningminutes, self.pctuiautomatormix, self.throttle)
        else:
            cmd = 'adb -s %s shell "CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar exec app_process /system/bin tv.panda.test.monkey.Monkey ' \
                  '-p %s --%s --running-minutes %s --ignore-crashes --ignore-timeouts --throttle %s -v -v -v -v > /sdcard/monkeyout.txt 2>/sdcard/monkeyerr.txt"' % (
                      self.serial, self.pkgname, self.mode, self.runningminutes, self.throttle)
        U.Logging.info(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        U.Logging.info("waiting for 10s")
        return process

    def __initialization_arrangement(self):
        #初始化log
        U.Logging.info("init logs in device %s" % self.serial)
        self.dl.init()
        al = l.Al(self.serial)
        al.main(self.dl.log_path)

        # 推送必要的jar包和配置文件到手机
        U.Logging.info("push the monkey jars to %s" % self.serial)
        process = self.adb.adb('push conf/lib/framework.jar /sdcard/')
        stdout, stderr = process.communicate()
        if 'error' in stdout:
            U.Logging.error(stdout)
            return False
        self.adb.adb('push conf/lib/monkey.jar /sdcard/')
        self.adb.adb('push conf/lib/max.config /sdcard/')
        self.adb.adb('shell rm /sdcard/crash-dump.log')

        return True


    def __install_app(self):
        if self.apk_path:
            if self.package.boolpkg:
                install = InstallApp(self.serial, self.package)
                login = LoginApp(self.serial, self.package)
                return install.run_install() and login.login_app()
            else:
                U.Logging.error('get package name failed and skip')
                return False
        else:
            U.Logging.info("apk_path is null so start app only")
            return True

    """
        启动遍历程序过程
        执行步骤:
            1:安装应用
            2:登录
            3:开启back逻辑
            4:执行遍历命令
        :return:
    """

    def run(self):
        if self.__initialization_arrangement() and self.__install_app():
            self.__start_back_strategy()
            self.process = self.__start_new_monkey()
            return True
        else:
            U.Logging.error("install failed skip other process")
            return False
