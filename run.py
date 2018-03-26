# -*- coding: utf-8 -*-
import sys

__author__ = 'xiaqing'

"""
@author:xiaqing
@time: 18/3/13 下午3:55
"""
import signal
import click
from po import integration
import public.Analyzelog as l
import lib.Utils as U


def sigint_handler(signum, frame):
    global is_sigint_up
    is_sigint_up = True
    print 'catched interrupt signal!'


signal.signal(signal.SIGINT, sigint_handler)
is_sigint_up = False


@click.group()
def cli():
    pass


@cli.command()
@click.option('-s', default="", prompt=u'-s 请指定一个或多个测试设备', help=u"设备id,支持多个设备同时，&分割")
@click.option('-p', default="", help=u"测试app的包名,-p与--apk至少要填写一个参数")
@click.option('--apk', default="", help=u"测试app的apk绝对路径,不填写则直接开始测试，请确保已经安装好app并进行登录")
@click.option('--mode', type=click.Choice(['uiautomatormix', 'uiautomatordfs']), default="uiautomatormix",
              help=u"uiautomatormix是随机点击控件加monkey模式，uiautomatordfs是遍历控件模式")
@click.option('--runningminutes', default="1", help=u"执行时间")
@click.option('--throttle', default="600", help=u"点击间隔")
@click.option('--pctuiautomatormix', default="70", help=u"仅仅只有uiautomatormix模式需要填写uiautomator和monkey的比例")
def run_monkey(s, p, apk, mode, runningminutes, throttle, pctuiautomatormix):
    processdic = {}
    # try:
    l.ProjectLog.set_up()
    if p or apk:
        snlist = s.split('&')
        for serial in snlist:
            ir = integration.RunMonkey(serial, p, apk, mode, runningminutes, throttle, pctuiautomatormix)
            # 成功启动再记录对象
            if ir.run():
                processdic[serial] = ir

        for serial in processdic:
            processdic[serial].process.wait()
            processdic[serial].dl.check()

            # 停止get back守护线程
            processdic[serial].man_talk_event.set()

            # 如果提供了apk路径就卸载app
            if apk:
                processdic[serial].adb.quit_app(processdic[serial].pkgname)
                processdic[serial].adb.remove_app(processdic[serial].pkgname)

        l.ProjectLog.tear_down()

    else:
        U.Logging.error(u"-p与--apk至少要填写一个参数")

        # except Exception, e:
        #     # 异常退出保存log
        #     U.Logging.error(e)
        #     for serial in processdic:
        #         processdic[serial].dl.check()
        #     l.ProjectLog.tear_down()


if __name__ == '__main__':
    cli(sys.argv[1:])
