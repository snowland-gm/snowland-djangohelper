#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: _base .py
# @time: 2020/12/8 0:01
# @Software: PyCharm


from django.db import models

__all__ = [
    'BaseModel'
]


class BaseModel(models.Model):
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True

    def __repr__(self):
        name = self.__class__.__name__
        s = ''.join('{}:({})\n'.format(attr, value)
                    for attr, value in self.__dict__.items() if not attr.startswith('_'))
        return '< {}\n{} >\n'.format(name, s)

    @classmethod
    def new(cls, form):
        m = cls()
        [setattr(m, name, value) for name, value in form.items() if value]
        m.save()
        return m

    @classmethod
    def update(cls, id_, **kwargs):
        m = cls.objects.get(id=id_)
        for name, value in kwargs.items():
            if isinstance(value, list):
                value = value[0]
            setattr(m, name, value)
        m.save()

    @classmethod
    def one(cls, **kwargs):
        return cls.objects.get(**kwargs)

    @classmethod
    def all(cls):
        return cls.objects.all()

    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.objects.filter(*args, **kwargs)
