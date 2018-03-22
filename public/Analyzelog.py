# -*- coding: utf-8 -*-

import filecmp
import re
import shutil
import datetime
import os
import lib.adbUtils
import time
import lib.Utils as U

__author__ = 'xiaqing'

"""
@author:xiaqing
@time: 16/11/15 下午1:44
"""



LOG_ROOT = "logs"
HISTORY_ROOT = "history_logs"


class Al:
    def __init__(self, device):
        self.device = device
        self.log_path = "{}/{}".format(LOG_ROOT, "logcat.log")

    def _get_android_log(self, log_path):
        """

        :return:清理当前设备缓存log,并且记录当前设备log
        """

        adb = lib.adbUtils.ADB(self.device)
        adb.c_logcat()
        adb.logcat(log_path)

    def main(self, log_path):
        """
            :return: 开启记录log
        """
        return self._get_android_log(log_path)


class ProjectLog:
    def __init__(self):
        self.log_root = LOG_ROOT
        self.log_path = "{}/{}".format(LOG_ROOT, "log.txt")
        self.history_root = HISTORY_ROOT

    @staticmethod
    def set_up():
        # 清理之前的项目日志目录
        if os.path.exists(LOG_ROOT):
            shutil.rmtree(LOG_ROOT)
        # 创建新的项目日志目录
        os.makedirs(LOG_ROOT)

        # 初始化logging
        # logging.basicConfig(
        #     level=logging.INFO,
        #     format="%(asctime)s %(levelname)s\t[%(threadName)s] %(message)s",
        #     datefmt="%Y-%m-%d %H:%M:%S",
        #     filename=self.log_path,
        #     filemode="w"
        # )

    @staticmethod
    def tear_down():
        # 创建历史结果目录
        if not os.path.exists(HISTORY_ROOT):
            os.makedirs(HISTORY_ROOT)
        # 将本次结果目录复制到历史结果目录
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dest_dir = os.path.join(HISTORY_ROOT, now)
        shutil.copytree(LOG_ROOT, dest_dir)


class DeviceLog:
    def __init__(self, sn, pkgname):
        self.sn = sn
        self.pkgname = pkgname
        self.device_root = "{}/{}".format(LOG_ROOT, self.sn)
        self.anr_dir = "{}/{}".format(self.device_root, "anr")
        self.crash_dir = "{}/{}".format(self.device_root, "crash")
        self.dump_dir = "{}/{}".format(self.device_root, "dumpsys")
        self.log_path = "{}/{}".format(self.device_root, "logcat.log")
        self.monkeyout = "{}/{}".format(self.device_root, "monkeyout.log")
        self.monkeyerr = "{}/{}".format(self.device_root, "monkeyerr.log")
        self.crashlog = "{}/{}".format(self.device_root, "dump-crash.log")

        # self.log_path = "/home/ren/monkey.log"

    def init(self):
        # 清理device之前的日志目录
        if os.path.exists(self.device_root):
            shutil.rmtree(self.device_root)
        # 创建device所需的日志目录
        os.makedirs(self.device_root)
        os.makedirs(self.anr_dir)
        os.makedirs(self.crash_dir)
        os.makedirs(self.dump_dir)

    def __get_logs(self):
        adb = lib.adbUtils.ADB(self.sn)
        adb.adb("pull /sdcard/monkeyout.txt %s" % self.monkeyout)
        adb.adb("pull /sdcard/monkeyerr.txt %s" % self.monkeyerr)
        adb.adb("pull /sdcard/crash-dump.log %s" % self.crashlog)
        time.sleep(5)

    @staticmethod
    def __remove_excess_traces(anr_info):
        # 获取PID
        pid = 0
        for line in anr_info:
            if line.startswith("PID: "):
                pid = re.findall(r"PID: (\d+)", line)[0]
                break
        # 获取anr traces起始、末尾行，对应pid的起始、末尾行:
        trace_start = 0
        trace_end = 0
        trace_pid_start = 0
        trace_pid_end = 0
        for i in range(len(anr_info)):
            line = anr_info[i]
            if "----- pid " in line and trace_start == 0:
                trace_start = i
            if "----- end " in line:
                trace_end = i
            if "----- pid %s " % pid in line and trace_pid_start == 0:
                trace_pid_start = i
            if "----- end %s " % pid in line and trace_pid_end == 0:
                trace_pid_end = i
        # 如果起始、末尾行有问题，则不处理
        if not (0 < trace_start <= trace_pid_start < trace_pid_end <= trace_end or
                    (trace_pid_start == trace_pid_end == 0 < trace_start < trace_end)):
            return anr_info
        # 处理保留信息
        anr_store = []
        for i in range(len(anr_info)):
            line = anr_info[i]
            if i < trace_start or i > trace_end or trace_pid_start <= i <= trace_pid_end:
                anr_store.append(line)
        return anr_store

    def check(self):
        #先取log在分析
        self.__get_logs()
        if not (os.path.exists(self.monkeyout) and os.path.exists(self.monkeyerr)):
            U.Logging.error("missing the log of %s" % self.monkeyout)
            return False

        time.sleep(3)
        with open(self.monkeyout, "r") as fp:
            # 判断文件行是否为anr或crash，如果是则做相关处理
            is_anr = 0
            is_crash = False
            # anr和crash计数
            anr_cnt = 0
            crash_cnt = 0
            # anr和crash信息
            anr_info = []
            crash_info = []
            # 逐行读取日志信息
            for line in fp:
                # ANR处理
                if line.startswith("// NOT RESPONDING: {} ".format(self.pkgname)):
                    if is_anr == 0:
                        anr_cnt += 1
                    is_anr += 1
                if is_anr != 0:
                    anr_info.append(line)
                if is_anr != 0 and line.strip() == "// meminfo status was 0":
                    is_anr -= 1
                    if is_anr == 0:
                        # 去掉多余的traces
                        anr_info = self.__remove_excess_traces(anr_info)
                        # 存成文件
                        filename = os.path.join(self.anr_dir, "anr_{}_{}.txt".format(self.sn, anr_cnt))
                        with open(filename, "w") as anr_fp:
                            for anr_line in anr_info:
                                anr_fp.write(anr_line)
                        # 清空
                        anr_info = []
                # CRASH处理
                if line.startswith("// CRASH: {} ".format(self.pkgname)) or line.startswith(
                        "// CRASH: {}:".format(self.pkgname)):
                    is_crash = True
                    crash_cnt += 1
                if is_crash:
                    crash_info.append(line)
                if is_crash and line.strip() == "//":
                    # 存成文件
                    filename = os.path.join(self.crash_dir, "crash_{}_{}.txt".format(self.sn, crash_cnt))
                    with open(filename, "w") as crash_fp:
                        for crash_line in crash_info[1:]:
                            crash_fp.write(crash_line)
                            U.Logging.error(crash_line)
                    # 清空
                    crash_info = []
                    is_crash = False

        with open(self.monkeyerr, "r") as fp:
            for line in fp:
                U.Logging.error(line)

    @staticmethod
    def __numerical_sort(value):
        numbers = re.compile(r"(\d+)")
        parts = numbers.split(value)
        parts[1::2] = map(int, parts[1::2])
        return parts

    def get(self):
        # 获取anr、crash、dumpsys
        anr_fn_list = os.listdir(self.anr_dir)
        anr_fn_list = sorted(anr_fn_list, key=self.__numerical_sort, reverse=False)
        anr_cnt = len(anr_fn_list)
        crash_fn_list = os.listdir(self.crash_dir)
        crash_fn_list = sorted(crash_fn_list, key=self.__numerical_sort, reverse=False)
        crash_cnt = len(crash_fn_list)
        dumpsys_fn_list = os.listdir(self.dump_dir)
        # 将anr、crash、dumpsys写入附件list
        att_list = []
        anr_dic = {}
        for fn_add in anr_fn_list:
            flag = True
            for fn in att_list:
                if filecmp.cmp(self.anr_dir + "/" + fn_add, fn):
                    fn_name = fn.split('/')[-1]
                    anr_dic[fn_name] = anr_dic[fn_name] + 1
                    flag = False
                    break
            if flag:
                anr_dic[fn_add] = 1
                att_list.append("{}/{}".format(self.anr_dir, fn_add))
        # for fn in anr_fn_list:
        #     att_list.append("{}/{}".format(self.anr_dir, fn))
        crash_dic = {}
        for fn_add in crash_fn_list:
            flag = True
            for fn in att_list:
                print filecmp.cmp(self.crash_dir + "/" + fn_add, fn)
                if filecmp.cmp(self.crash_dir + "/" + fn_add, fn):
                    fn_name = fn.split('/')[-1]
                    crash_dic[fn_name] = crash_dic[fn_name] + 1
                    flag = False
                    break
            if flag:
                crash_dic[fn_add] = 1
                f = open("{}/{}".format(self.crash_dir, fn_add), 'r')
                firstline = f.readline()
                pa = re.compile(r"leakcanary")
                if not pa.match(firstline):
                    att_list.append("{}/{}".format(self.crash_dir, fn_add))
        print crash_dic, att_list
        # for fn in crash_fn_list:
        #     att_list.append("{}/{}".format(self.crash_dir, fn))
        for fn in dumpsys_fn_list:
            att_list.append("{}/{}".format(self.dump_dir, fn))
        # 返回anr_cnt、crash_cnt和att_list
        return anr_cnt, crash_cnt, att_list, anr_dic, crash_dic


if __name__ == '__main__':
    log = DeviceLog('0623ea5a00609f1f')
    log.check("com.cmcm.shorts")