#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/7 0007 上午 1:54
# @Author  : 河北雪域网络科技有限公司 A.Star
# @Site    : 
# @File    : createAdmin.py
# @Software: PyCharm

def create_admin(modelname='models.py', adminname='admin_new.py', list_per_page = 10):
    lines = []
    with open(modelname, "r") as f:
        lines = f.readlines()
    items = []
    classnames = []
    with open(adminname, "w+") as f:
        f.write("from django.contrib import admin\n")
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
                    f.write('    list_per_page = '+str(list_per_page)+"\n\n")
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
        [f.write("admin.site.register(models."+classname+", "+classname+"Admin)\n") for classname in classnames]


if __name__ == '__main__':
    create_admin()