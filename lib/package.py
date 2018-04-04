#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import re
import lib.Utils as U
import platform

# 判断系统类型，windows使用findstr，linux使用grep
system = platform.system()
if system is "Windows":
    find_util = "findstr"
    aapt = 'conf\\lib\\aapt.exe'
else:
    find_util = "grep"
    aapt = 'conf/lib/aapt'

class Package:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.name = ""
        self.activity = ""
        self.version_code = ""
        self.boolpkg = self.__get_package()

    def __get_package(self):
        # 判断是否有apk，如果没有则说明下载异常返回false
        if self.apk_path.endswith("apk") and os.path.exists(self.apk_path):
            if self.__set_pkg_info():
                return True
            else:
                return False
        else:
            return False


    def __set_pkg_info(self):
        # 获取文件名
        self.apk_name = os.path.basename(self.apk_path)
        aaptpath = os.path.join(os.path.abspath(os.path.join(os.getcwd())),aapt)

        # 获取包名
        cmd = '{} dump badging "{}" | {} package'.format(aaptpath, self.apk_path, find_util)
        process = U.cmd(cmd)
        stdout, stderr = process.communicate()
        if stdout is None:
            U.Logging.error("[pkg_info] time out: {}".format(cmd))
        elif "ERROR" in stderr or "error" in stderr:
            U.Logging.error("[pkg_info] cannot execute: {}".format(cmd))
            U.Logging.error("[pkg_info] result: {}".format(stderr))
        else:
            try:
                package_name = re.findall(r"name='([a-zA-Z0-9.*]+)'", stdout)
                self.name = package_name[0]
                self.version_code = re.findall(r"versionCode='([0-9]+)'", stdout)[0]
            except Exception as e:
                U.Logging.error("[pkg_info] failed to regex package name from {}. {}".format(stdout, e))
        # 获取启动Activity
        cmd = '{} dump badging "{}" | {} launchable-activity'.format(aaptpath, self.apk_path, find_util)
        process = U.cmd(cmd)
        stdout, stderr = process.communicate()
        if stdout is None:
            U.Logging.error("[pkg_info] time out: {}".format(cmd))
        elif "ERROR" in stderr or "error" in stderr:
            U.Logging.error("[pkg_info] cannot execute: {}".format(cmd))
            U.Logging.error("[pkg_info] result: {}".format(stderr))
        else:
            try:
                activity_list = re.findall(r"name='(.+?)'", stdout)
                main_activity = ""
                for activity in activity_list:
                    if not activity.startswith("com.squareup") and not activity.startswith("com.github"):
                        main_activity = activity
                        break
                self.activity = main_activity
            except Exception as e:
                U.Logging.error("[pkg_info] failed to regex main activity from {}. {}".format(stdout, e))

        if self.name and self.activity:
            return True

        return False





