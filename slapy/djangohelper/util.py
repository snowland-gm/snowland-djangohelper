#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: util.py
# @time: 2018/7/23 14:46
# @Software: PyCharm

import html.parser as HTMLParser

from bs4 import BeautifulSoup
import glob
import os
import re


def create_admin(modelname='models.py', adminname='admin_new.py', list_per_page=10, encoding='utf8'):
    """
    根据models生成admin
    :param modelname:
    :param adminname:
    :param list_per_page:
    :param encoding:
    :return:
    """
    lines = []
    with open(modelname, "r", encoding=encoding) as f:
        lines = f.readlines()
    items = []
    classnames = []
    with open(adminname, "w+", encoding=encoding) as f:
        f.write("from django.contrib import admin\n")
        f.write("from . import models\n\n")
        for eachline in lines:
            eachline = eachline.split('#')[0]

            if eachline.startswith("class"):
                if items:
                    f.write("    list_display = ('id',")
                    [f.write(" '" + item + "',") for item in items]
                    f.write(')\n')
                    f.write("    list_editable = (")
                    [f.write("'" + item + "',") for item in items]
                    f.write(')\n')
                    f.write('    list_per_page = ' + str(list_per_page) + "\n\n")
                items = []
                classname = eachline.split('(')[0][6:]
                classnames.append(classname)
                f.write('class ' + classname + 'Admin(admin.ModelAdmin):\n')
            elif eachline.find('=') > 0:
                splited = eachline.split('=')
                item = splited[0].replace(' ', '')
                if item != '' and item != "\n":
                    items.append(item)

        if items:
            f.write("    list_display = ('id',")
            [f.write(" '" + item + "',") for item in items]
            f.write(')\n')
            f.write("    list_editable = (")
            [f.write(" '" + item + "',") for item in items]
            f.write(')\n')

        f.write("\n\n")
        [f.write("admin.site.register(models." + classname + ", " + classname + "Admin)\n") for classname in classnames]


trans_list = ['.html', '.htm']


def trans_file(file):
    splitext = os.path.splitext(file)
    with open(file, "r", encoding='utf-8') as f1, open("{}.bak".format(splitext[0]), "w", encoding='utf-8') as f2:
        for line in f1:
            if "<title>" in line:
                f2.write("{% load staticfiles %}\n")
            n_line = trans_href(line)
            n_line = trans_src(n_line)
            f2.write(n_line)

    os.remove(file)
    os.rename("{}.bak".format(splitext[0]), file)


def trans_href(s):
    pattern_href = re.compile('href=[\"|\'].*?\.css[\"|\']')
    str_href = re.findall(pattern_href, s)
    if str_href and (str(str_href).startswith('http')):
        str_href = str_href[0][6:-1]
        s = s.replace(str_href, "{%static '" + str_href + "'%}")
    return s


def trans_src(s):
    pattern_src = re.compile('src=".*?[\.js|\.css|\.png\.jpg|\.bmp|\.gif]"')
    str_src = re.findall(pattern_src, s)
    if str_src and (not str(str_src).startswith('http')):
        str_src = str_src[0][5:-1]
        s = s.replace(str_src, "{%static '" + str_src + "'%}")
    return s


def trans(root):
    files = [root + '/' + i for i in os.listdir(root) if
             os.path.isfile(root + '/' + i) and os.path.splitext(i)[1] in trans_list]

    [trans_file(file) for file in files]


def traversalDir_FirstDir(path):
    mlist = []
    if (os.path.exists(path)):
        # 获取该目录下的所有文件或文件夹目录路径
        files = glob.glob(path + '\\*')
        # print(files)
        for file in files:
            # 判断该路径下是否是文件夹
            if (os.path.isdir(file)):
                mlist.extend(traversalDir_FirstDir(file))
            else:
                (filepath, tempfilename) = os.path.split(file)
                mlist.append(tempfilename)
    return mlist


def createView(templetesPath, viewPath, encoding="utf8"):
    with open(viewPath, "w+", encoding=encoding) as f:
        f.write('from django.shortcuts import render, render_to_response\n')
        f.write('import json\n\n\n')
        mlist = traversalDir_FirstDir(templetesPath)
        for each in mlist:
            (shotname, extension) = os.path.splitext(each)
            f.write("def " + shotname + "(req):\n")
            f.write("    return render_to_response('" + each + "')\n\n")


if __name__ == '__main__':
    create_admin()
