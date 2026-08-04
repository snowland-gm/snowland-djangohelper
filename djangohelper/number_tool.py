#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: number_tool.py
# @time: 2019/3/11 16:58
# @Software: PyCharm


__author__ = 'A.Star'


import secrets

hex_string = '0123456789abcdef'
hex_string_upper = '0123456789ABCDEF'
alnum_string = 'qwertyuiopasdfghjklzxcvbnm1234567890'


def random_string(n: int = 32, allow_chars: str = alnum_string) -> str:
    """Generate a random string of length ``n`` from ``allow_chars``.

    Uses :class:`secrets.SystemRandom` for cryptographically stronger
    randomness (equivalent to the previous ``astartool.random`` behaviour).
    """
    r = secrets.SystemRandom()
    return ''.join(r.choices(allow_chars, k=n))


def random_hex_string(n: int = 32, upper: bool = False) -> str:
    """Generate a random hexadecimal string of length ``n``."""
    r = secrets.SystemRandom()
    charset = hex_string_upper if upper else hex_string
    return ''.join(r.choices(charset, k=n))
