"""Tests for djangohelper.common (global constants and demos)."""
from djangohelper import common


def test_error_codes():
    assert common.ERROR_CODE_UNKNOWN == -1
    assert common.ERROR_CODE_OPERATION_FAILED == 0
    assert common.ERROR_CODE_OPERATION_SUCCESS == 1
    assert common.ERROR_CODE_PARTNER_ERROR == 2
    assert common.ERROR_CODE_TOKEN_ERROR == 3
    assert common.ERROR_CODE_DATABASE_ERROR == 4
    assert common.ERROR_CODE_LOGINED_ERROR == 5
    assert common.ERROR_CODE_ACCOUNT_LOCKED_ERROR == 6
    assert common.ERROR_CODE_IP_TRY_TIME_LIMITED_ERROR == 7
    assert common.ERROR_CODE_ACCOUNT_TRY_TIME_LIMITED_ERROR == 8
    assert common.ERROR_CODE_SERVER_ERROR == 99


def test_json_demo_keys():
    assert set(common.JSON_DEMO.keys()) == {'successful', 'data', 'code', 'message'}


def test_payload_demo_keys():
    assert set(common.PAYLOAD_DEMO.keys()) == {
        'iss', 'sub', 'aud', 'exp', 'nbf', 'iat', 'jti'
    }


def test_extension_lists():
    assert '.py' in common.list_allow_extension
    assert '.git' in common.list_ignore
