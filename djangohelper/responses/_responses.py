#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: responses .py
# @time: 2021/1/9 17:49
# @Software: PyCharm

from rest_framework.response import Response

__all__ = [
    'APIResponse'
]

from rest_framework import viewsets, status, permissions

from djangohelper.common import *

from rest_framework.response import Response


class APIResponse(Response):

    def __init__(self, data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type='application/json; charset=utf-8',
                 successful=True, code=ERROR_CODE_OPERATION_SUCCESS, message=None):
        data = {
            'successful': successful,
            'code': code,
            'message': message,
            'data': data
        }

        super().__init__(data=data, status=status, template_name=template_name, headers=headers, exception=exception,
                         content_type=content_type)
