# coding: utf-8

from rest_framework.pagination import PageNumberPagination

from djangohelper.responses import APIResponse


class BasePageNumberPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        return APIResponse(data={
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })