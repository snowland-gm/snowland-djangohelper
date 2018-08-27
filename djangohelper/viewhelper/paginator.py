#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: paginator.py
# @time: 2018/8/27 17:56
# @Software: PyCharm
import json
from django.core import serializers
from django.core.paginator import Paginator


def generate_paginator_result(queryset, per_page, orphans=0,
                              allow_empty_first_page=True, length_pagequeue=5, page=1):
    """

    :param queryset:
    :param per_page:
    :param orphans:
    :param allow_empty_first_page:
    :param length_pagequeue:
    :param page:
    :return:
    """
    temp_list = json.loads(serializers.serialize('json', queryset))
    paginator = Paginator(temp_list, per_page, orphans, allow_empty_first_page)
    contacts = paginator.page(page)
    num_pages = contacts.paginator.num_pages
    if num_pages < 5:
        list_show = list(range(1, num_pages + 1))
    elif num_pages - page >= length_pagequeue:
        list_show = list(range(page, page + length_pagequeue))
    else:
        list_show = list(range(num_pages - length_pagequeue + 1, num_pages + 1))

    res_dict = {
        'contacts': contacts,
        "ind": list_show,
    }
    return res_dict
