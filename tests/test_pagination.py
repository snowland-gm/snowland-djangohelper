"""Tests for djangohelper.pagination.BasePageNumberPagination."""
from unittest import mock

from djangohelper.pagination import BasePageNumberPagination


def test_get_paginated_response():
    pg = BasePageNumberPagination()
    pg.page = mock.Mock()
    pg.page.paginator.count = 10
    pg.get_next_link = lambda: 'http://next'
    pg.get_previous_link = lambda: None

    resp = pg.get_paginated_response([1, 2, 3])
    data = resp.data
    assert data['successful'] is True
    assert data['data']['count'] == 10
    assert data['data']['results'] == [1, 2, 3]
    assert data['data']['next'] == 'http://next'
    assert data['data']['previous'] is None
