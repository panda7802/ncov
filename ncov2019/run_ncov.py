# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import subprocess
import sys
import time

import django
from scrapy import cmdline
from multiprocessing import Process


def get_2019ncov():
    """
    获取历史列表
    :return:
    """
    args = "scrapy crawl get_his".split()
    cmdline.execute(args)
    # subprocess.Popen(args)


def get_ncov_city():
    """
    获取城市历史列表
    :return:
    """
    args = "scrapy crawl city_his".split()
    cmdline.execute(args)
    # subprocess.Popen(args)


if __name__ == '__main__':
    DJANGO_PROJECT_PATH = '../../lxdzx_server'
    DJANGO_SETTINGS_MODULE = 'lxdzx_server.settings'
    sys.path.insert(0, DJANGO_PROJECT_PATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE    )
    # application = django.core.handlers.wsgi.WSGIHandler()
    print("===========setting over===========")
    django.setup()

    # get_2019ncov()
    get_ncov_city()

    # while True:
    #     print("------------")
    #     p = Process(target=get_2019ncov)
    #     p.start()
    #     p.join()
    #     print("------next------")
    #     time.sleep(60)
