#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: permission .py
# @time: 2020/8/19 2:58
# @Software: PyCharm

from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):
    """为管理员分组成员"""

    def has_permission(self, request, view):
        # 获取当前登陆用户
        user = request.user
        # 如果未登录，返回False --> 无权限
        if not user or user.is_anonymous:
            return False
        # 判断用户是否是管理分组的用户(管理员分组是Group表中的一条自定义记录)
        # 如果不是返回False --> 无权限
        if not user.groups.filter(name='管理员'):
            return False
        return user.is_superuser


class AuditPermission(BasePermission):
    def has_permission(self, request, view):
        # 获取当前登陆用户
        user = request.user
        # 如果未登录，返回False --> 无权限
        if not user or user.is_anonymous:
            return False
        return user.is_auditor or user.is_superuser


class OperatorPermission(BasePermission):
    """操作员"""

    def has_permission(self, request, view):
        # 获取当前登陆用户
        user = request.user
        # 如果未登录，返回False --> 无权限
        if not user or user.is_anonymous:
            return False
        return user.is_operator or user.is_superuser


class SuperuserPermission(BasePermission):
    def has_permission(self, request, view):
        # 获取当前登陆用户
        user = request.user
        # 如果未登录，返回False --> 无权限
        if not user or user.is_anonymous:
            return False
        return user.is_superuser


class AllPermission(BasePermission):
    def has_permission(self, request, view):
        # 获取当前登陆用户
        user = request.user
        # 如果未登录，返回False --> 无权限
        return user and user.is_authenticated
