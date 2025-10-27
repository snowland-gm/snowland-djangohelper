#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: number_tool.py
# @time: 2019/3/11 16:58
# @Software: PyCharm


__author__ = 'A.Star'


from astartool.random import random_string as random_string_astartool, random_hex_string as random_hex_string_astartool

hex_string = '0123456789abcdef'
hex_string_upper = '0123456789ABCDEF'
alnum_string = 'qwertyuiopasdfghjklzxcvbnm1234567890'


random_hex_string = random_hex_string_astartool

def random_string(n: int = 32):
    return random_string_astartool(n, alnum_string)
