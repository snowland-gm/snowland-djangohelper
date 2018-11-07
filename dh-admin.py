#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: dh-admin.py
# @time: 2018/9/2 0:11
# @Software: PyCharm

import sys
import os

if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) == 1:
        profix = "snowland_"

    product_name = sys.argv[0]
    # os.makedirs(product_name)
    # os.start
    os.system("django-admin startproject " + profix + product_name)
    os.system("cd " + profix + product_name)
    os.system("django-admin startapp " + product_name)
    os.system("cd ..")
    content = """<uwsgi>
                <socket>:8080</socket>
                <chdir>/opt/snowland/python/"""
    + product_name
    + """</chdir>
                    <module>django_wsgi</module>
                    <processes>4</processes> <!-- 进程数 --> 
                    <daemonize>uwsgi.log</daemonize>
                </uwsgi>"""

    with open("django_socket.xml", "w+") as f:
        f.writelines(content)

