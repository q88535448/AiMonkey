# -*- coding: utf-8 -*-
import lib.adbUtils
from time import sleep
import datetime
import threading
import lib.Utils as U


class r(threading.Thread):
    def __init__(self, serial, runningminutes, throttle, package):
        threading.Thread.__init__(self)
        self.serial = serial
        self.runningminutes = runningminutes
        self.throttle = float(throttle) / 1000
        self.package = package

    def run(self):
        # 等待遍历程序启动
        sleep(15)
        act_diff = ""
        act_num = 0
        activity_dic = {}
        time_start = datetime.datetime.now()
        adb = lib.adbUtils.ADB(self.serial)

        while True:
            try:
                activity = adb.get_current_activity()
            except Exception as e:
                U.Logging.error(e)
                continue
            U.Logging.debug(activity)

            if activity in activity_dic:
                activity_dic[activity] += 1
            else:
                activity_dic[activity] = 1

            time_finish = datetime.datetime.now()
            during = (time_finish - time_start).seconds

            # 实际执行时间大于runningminutes时间则退出线程
            if during > self.runningminutes * 60:
                break

            sleep(self.throttle)
            # 每隔10s进行一次判断如果处于同一个activity则back
            if during % 10 == 0:
                if act_diff == activity:
                    U.Logging.warn("10s activity 未发生改变，get back")
                    adb.send_key_event("4")
                else:
                    act_diff = activity

                for act in activity_dic:
                    U.Logging.info('%s %s' % (act, activity_dic[act]))

            if during % 300 == 0 and during != 0:
                if act_num < len(activity_dic):
                    act_num = len(activity_dic)
                else:
                    U.Logging.warn("当前已遍历activity：%s 5分钟未增长，返回首页" % len(activity_dic))
                    if self.package:
                        adb.start_activity('%s/%s' % (self.package.name, self.package.activity))
