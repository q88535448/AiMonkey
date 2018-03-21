# -*- coding: utf-8 -*-
import lib.adbUtils
import re
import lib.Utils as U
__author__ = 'xiaqing'

"""
@author:xiaqing
@time: 16/11/15 下午1:44
"""


class InstallApp:
    def __init__(self, serial, package):
        self.package = package
        self.serial = serial

    def run_install(self):
        adb = lib.adbUtils.ADB(self.serial)
        api_level = adb.get_api_level()
        if adb.is_install(self.package.name):
            adb.remove_app(self.package.name)

        opts = "-g " if int(api_level) > 22 else ""  # grant all runtime permissions for api>=21
        U.Logging.info("start install app for %s" % self.serial)
        process = adb.adb("-s %s install -r %s '%s'" % (self.serial, opts, self.package.apk_path))
        stdout, stderr = process.communicate()
        fails = re.findall(r"Failure\s[[][\w|\W]+[]]", stdout)
        if fails:
            U.Logging.error(fails)

        if adb.is_install(self.package.name):
            return True
        else:
            return False
