#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: common.py
# @time: 2018/10/29 10:24
# @Software: PyCharm


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

ERROR_CODE_UNKNOWN = -1  # 未知错误
ERROR_CODE_OPERATION_FAILED = 0  # 操作失败
ERROR_CODE_OPERATION_SUCCESS = 1  # 操作成功
ERROR_CODE_PARTNER_ERROR = 2  # 参数有误
ERROR_CODE_TOKEN_ERROR = 3  # token失效
ERROR_CODE_DATABASE_ERROR = 4  # 数据库错误
ERROR_CODE_LOGINED_ERROR = 5  # 该账户已在其他设备登录，已退出
ERROR_CODE_ACCOUNT_LOCKED_ERROR = 6  #	账户被锁定、禁用|
ERROR_CODE_IP_TRY_TIME_LIMITED_ERROR = 7  # 同一终端登录失败次数超过限制|
ERROR_CODE_ACCOUNT_TRY_TIME_LIMITED_ERROR = 8  # 同一账户登录失败次数超过限制|
ERROR_CODE_SERVER_ERROR = 99  # 后台处于维护状态|
