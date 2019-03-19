#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: number_tool.py
# @time: 2019/3/11 16:58
# @Software: PyCharm


__author__ = 'A.Star'

from random import choices

hex_string = '0123456789abcdef'
hex_string_upper = '0123456789ABCDEF'
alnum_string = 'qwertyuiopasdfghjklzxcvbnm1234567890'

def random_hex_string(n:int=32, upper=False):
    return ''.join(choices(hex_string_upper, k=n)) if upper else ''.join(choices(hex_string, k=n))

def random_string(n: int = 32):
    return ''.join(choices(alnum_string, k=n))
