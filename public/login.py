# -*- coding: utf-8 -*-

from uiautomator import Device
from lib.adbUtils import ADB
import lib.Utils as U
import time
__author__ = 'xiaqing'

"""
@author:xiaqing
@time: 16/11/15 下午1:44
"""

def click_premission(d):
    alerts = ['ALLOW', 'SKIP', 'OK', 'NEXT TIME','YES']
    num = 3
    while num > 0:
        for alert in alerts:
            if d(text=alert).exists:
                d(text=alert).click()
        num -= 1

class LoginApp:
    def __init__(self, serial, package):
        self.serial = serial
        self.package = package
        self.adb = ADB(serial)

    def login_app(self):
        d = Device('{}'.format(self.serial))
        component = "%s/%s" % (self.package.name, self.package.activity)
        self.adb.start_activity(component)
        time.sleep(15)

        try:
            if self.package.name == "com.cmcm.shorts":
                click_premission(d)
                d(resourceId="com.cmcm.shorts:id/home_bottom_user").click()
                d(resourceId="com.cmcm.shorts:id/layout_login_second").click()
                click_premission(d)
                # d(text="Guoliang Ren").click()
                d(resourceId="com.google.android.gms:id/account_name").click()
                time.sleep(15)
                click_premission(d)
                d.press.home()
            elif self.package.name == "com.cmcm.live":
                click_premission(d)
                d(resourceId="com.cmcm.live:id/layout_login_fifth").click()
                d(resourceId="com.cmcm.live:id/id_google_plus").click()
                click_premission(d)
                # d(text="Guoliang Ren").click()
                d(resourceId="com.google.android.gms:id/account_name").click()
                time.sleep(20)
                click_premission(d)
                d.press.home()
            elif self.package.name == "panda.keyboard.emoji.theme":
                d.click(770, 2100)
                time.sleep(2)
                d.press.back()
                time.sleep(2)
                d(text=' Cheetah Keyboard ❤ ❤ ❤ ').click()
                d(text='OK').click()
                d(text='OK').click()
                time.sleep(5)
                d.click(770, 2100)
                d(text=' Cheetah Keyboard ❤ ❤ ❤ ').click()
                time.sleep(5)
                click_premission(d)
                d.press.back()
                d.press.back()
                d.press.back()
            elif self.package.name == 'com.ksmobile.launcher':
                self.adb.quit_app(self.package.name)
                time.sleep(3)
                self.adb.start_activity(component)
                time.sleep(3)
                self.adb.send_key_event(3)
                d(resourceId="android:id/title").click()
                time.sleep(3)
                d(text="CM Launcher").click()
                time.sleep(3)
                d(text="Always").click()
            else:
                U.Logging.info("Don't need login")
            return True
        except Exception as e:
            U.Logging.error(e)
            U.Logging.error("login failed please check")
            return False


if __name__ == '__main__':
    import lib.package
    package = lib.package.Package('/Users/xiaqing/PycharmProjects/PrivateCloudAutotestPlatform/apks/Launcher/launcher_2018-03-09_17-59-42_r_v52210_official%28no_channel%29_resguard.apk')
    package.get_package()
    login = LoginApp('0623ea5a00609f1f', package)
    login.login_app()