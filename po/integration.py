# -*- coding: utf-8 -*-


from po import getback_strategy
import lib.Utils as U
import subprocess
import public.Analyzelog as l
import lib.package as pkg
from public.InstallApp import InstallApp
from public.login import LoginApp
from lib.adbUtils import ADB

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
        self.package = pkg.Package(self.apk_path)
        if apk_path:
            self.pkgname = self.package.name
        else:
            self.pkgname = pkgname
        self.dl = l.DeviceLog(serial, self.package.name)

    def __start_back_strategy(self):
        U.Logging.info("start the thread of getback_strategy")
        test_run = getback_strategy.r(self.serial, int(self.runningminutes), self.throttle, self.package)
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
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1,
                                   close_fds=True)

        U.Logging.info("waiting for 10s")
        return process

    def __initialization_arrangement(self):
        l.ProjectLog.set_up()
        self.dl.init()
        al = l.Al(self.serial)
        al.main(self.dl.log_path)

        U.Logging.info("push the monkey jars to %s" % self.serial)
        cmd = 'adb -s %s push conf/lib/framework.jar /sdcard/' % self.serial
        U.cmd(cmd)
        cmd = 'adb  -s %s push conf/lib/monkey.jar /sdcard/' % self.serial
        U.cmd(cmd)
        cmd = 'adb  -s %s push conf/lib/max.config /sdcard/' % self.serial
        U.cmd(cmd)
        cmd = 'adb  -s %s shell rm /sdcard/crash-dump.log' % self.serial
        U.cmd(cmd)
        U.Logging.info("init logs in device %s" % self.serial)


    def __install_app(self):
        if self.apk_path:
            if self.package.get_package():
                install = InstallApp(self.serial, self.package)
                login = LoginApp(self.serial, self.package.name)
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
            1:开启back逻辑
            2:执行遍历命令
            3:安装应用
            4:登录
        :return:
    """

    def run(self):
        self.__initialization_arrangement()
        if self.__install_app():
            self.__start_back_strategy()
            self.process = self.__start_new_monkey()
        else:
            U.Logging.error("install failed skip other process")
