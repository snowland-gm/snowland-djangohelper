#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/2 0002 下午 3:58
# @Author  : 河北雪域网络科技有限公司 A.Star
# @Site    : 
# @File    : utils.py
# @Software: PyCharm

import os.path
import glob
def traversalDir_FirstDir(path):
    mlist = []
    if (os.path.exists(path)):
    #获取该目录下的所有文件或文件夹目录路径
        files = glob.glob(path + '\\*' )
        # print(files)
        for file in files:
            #判断该路径下是否是文件夹
            if (os.path.isdir(file)):
                mlist.extend(traversalDir_FirstDir(file))
            else:
                (filepath, tempfilename) = os.path.split(file)
                mlist.append(tempfilename)
    return mlist
def createView(templetesPath, viewPath):
    with open(viewPath, "w+") as f:
        f.write('from django.shortcuts import render, render_to_response\n')
        f.write('import json\n\n\n')
        mlist = traversalDir_FirstDir(templetesPath)
        for each in mlist:
            (shotname, extension) = os.path.splitext(each)
            f.write("def "+shotname + "(req):\n")
            f.write("    return render_to_response('"+each+"')\n\n")


if __name__ == '__main__':
    createView("xmx_Homepage/templates", "xmx_Homepage/views.py")