#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: project2lines.py
# @time: 2018/8/1 15:49
# @Software: PyCharm

import os
import warnings
from djangohelper.common import list_allow_extension
import re


def file_to_lines(src_file,
                  to_file='out.txt',
                  start_file='\n',
                  end_file='\n'):
    """
    文件打印到字符串中
    :param src_file: 源文件
    :param to_file: 目标文件
    :param start_file: 文件头
    :param end_file: 文件尾
    :return:
    """
    with open(to_file, 'a+', encoding='utf-8') as outfile, open(src_file, 'rb') as infile:
        lines = infile.readlines()
        try:
            lines = [each_line.decode('gbk') for each_line in lines]
        except BaseException as e:
            # print(e)
            try:
                lines = [each_line.decode('utf8') for each_line in lines]
            except BaseException as e:
                # print(e)
                return
                # lines = [each_line.decode('unicode') for each_line in lines]
        outfile.write(src_file)
        outfile.write('\n')
        outfile.write(start_file)
        outfile.writelines(lines)
        outfile.write(end_file)


def walk(root,
         to_file='out.txt',
         start_file='\n',
         end_file='\n',
         allow_extension=list_allow_extension,
         ignore=list_ignore):
    for i in os.listdir(root):
        flag = True
        for each in ignore:
            if '*' in each:
                try:
                    if re.findall(each, i):
                        flag = False
                        break
                except:
                    pass
            else:
                if i == each or (i == each[:-1] and each.endswith('/')):
                    flag = False
                    break
        if flag:
            src_file = os.path.join(root, i)
            if os.path.isfile(src_file):
                if os.path.splitext(src_file)[1] in allow_extension and src_file not in ignore:
                    file_to_lines(src_file=src_file,
                                  to_file=to_file,
                                  start_file=start_file,
                                  end_file=end_file
                                  )
            else:
                walk(src_file,
                     to_file,
                     start_file,
                     end_file,
                     allow_extension,
                     ignore)


def project_to_lines(src_project,
                     to_file='out.txt',
                     start_file='\n',
                     end_file='\n',
                     allow_extension=list_allow_extension,
                     ignore=list_ignore):
    """
    项目打印为文件（申请软著用）
    :param src_project: 源文件项目根目录
    :param to_file: 转化到的文件名
    :param start_file: 文件开始
    :param end_file: 文件结束
    :param allow_extension: 需要转换的文件后缀
    :param ignore: 忽略转换的文件和文件夹
    :return:
    """
    if os.path.exists(to_file):
        warnings.warn('file ' + to_file + ' exist')
        txt = input('remove file?\n[Y]yes\n[N]no\n')
        if txt[0] is 'Y' or txt[0] is 'y':
            os.remove(to_file)
        else:
            return
    walk(src_project,
         to_file,
         start_file,
         end_file,
         allow_extension,
         ignore)


if __name__ == '__main__':
    project_to_lines(src_project='E:/cxl/codes/python/snowland-algorithm-python',
                     # start_file='\n' + '-' * 15 + '\n',
                     # end_file='\n' + '-' * 15 + '\n\n'
                     allow_extension=['.py',
                                      '.jl',
                                      '.m',
                                      '.js',
                                      '.java',
                                      '.xml',
                                      '.html',
                                      '.htm',
                                      '.css',
                                      '.cs',
                                      '.cpp',
                                      '.c',
                                      '.h',
                                      '.php'],
                    ignore=[]
                     )
