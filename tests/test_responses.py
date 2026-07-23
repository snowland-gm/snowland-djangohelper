"""Tests for djangohelper.responses.APIResponse."""
from djangohelper.common import ERROR_CODE_OPERATION_SUCCESS
from djangohelper.responses import APIResponse


def test_api_response_default():
    r = APIResponse(data={'a': 1})
    assert r.data['successful'] is True
    assert r.data['code'] == ERROR_CODE_OPERATION_SUCCESS
    assert r.data['message'] is None
    assert r.data['data'] == {'a': 1}


def test_api_response_custom():
    r = APIResponse(data={'x': 2}, successful=False, code=3, message='err')
    assert r.data == {
        'successful': False,
        'code': 3,
        'message': 'err',
        'data': {'x': 2},
    }
