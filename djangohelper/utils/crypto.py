#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: crypto.py
# @time: 2018/11/16 11:38
# @Software: PyCharm

import pysmx
from django.utils.crypto import pbkdf2 as pbkdf2_dj


def pbkdf2(password, salt, iterations, dklen=0, digest=pysmx.SM3.SM3Type):
    """Return the hash of password using pbkdf2."""
    return pbkdf2_dj(password, salt, iterations, dklen, digest)
