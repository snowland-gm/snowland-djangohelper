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

list_allow_extension = [
    '.py',
    '.jl',
    '.m',
    '.js',
    '.java',
    '.xml',
    '.html',
    '.htm',
    '.css',
    '.txt',
    '.cs',
    '.cpp',
    '.c',
    '.h',
    '.php'
]


def file_to_lines(src_file,
                  to_file='out.txt',
                  start_file='\n',
                  end_file='\n'):
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


def project_to_lines(src_project,
                     to_file='out.txt',
                     start_file='\n',
                     end_file='\n',
                     allow_extension=list_allow_extension):
    if os.path.exists(to_file):
        warnings.warn('file ' + to_file + ' exist')
        txt = input('remove file?\n[Y]yes\n[N]no\n')
        if txt[0] is 'Y' or txt[0] is 'y':
            os.remove(to_file)
        else:
            return
    for root, dirs, files in os.walk(src_project):
        for each_file in files:
            src_file = root + '/' + each_file
            if os.path.splitext(src_file)[1] in allow_extension:
                file_to_lines(src_file=src_file,
                              to_file=to_file,
                              start_file=start_file,
                              end_file=end_file
                              )


if __name__ == '__main__':
    project_to_lines(src_project='E:/cxl/codes/python/astardownload',
                     start_file='\n' + '-' * 15 + '\n',
                     end_file='\n' + '-' * 15 + '\n\n'
                     )
