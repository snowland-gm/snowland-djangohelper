"""Tests for djangohelper.permissions."""
from unittest import mock

from django.contrib.auth.models import AnonymousUser

# NOTE: djangohelper.permissions.__init__ does not re-export these classes,
# so we import them from the implementing module.
from djangohelper.permissions._permissions import (
    AdminPermission,
    AllPermission,
    AuditPermission,
    OperatorPermission,
    SuperuserPermission,
)


def _make_user(is_anonymous=False, is_superuser=False,
               is_auditor=False, is_operator=False, is_authenticated=True,
               in_admin_group=False):
    """Build a fake user whose boolean attributes are real booleans."""
    u = mock.MagicMock()
    u.is_anonymous = is_anonymous
    u.is_superuser = is_superuser
    u.is_auditor = is_auditor
    u.is_operator = is_operator
    u.is_authenticated = is_authenticated
    # AdminPermission checks membership of the '管理员' group.
    u.groups.filter.return_value = [1] if in_admin_group else []
    return u


def _request(user):
    return mock.MagicMock(user=user)


def test_anonymous_denied_for_all():
    anon = AnonymousUser()
    for perm in (
        AdminPermission(),
        AuditPermission(),
        OperatorPermission(),
        SuperuserPermission(),
        AllPermission(),
    ):
        assert perm.has_permission(_request(anon), None) is False


def test_superuser_allowed():
    u = _make_user(is_superuser=True, in_admin_group=True)
    assert SuperuserPermission().has_permission(_request(u), None) is True
    assert AdminPermission().has_permission(_request(u), None) is True
    assert AuditPermission().has_permission(_request(u), None) is True
    assert OperatorPermission().has_permission(_request(u), None) is True


def test_audit_permission():
    u = _make_user(is_auditor=True)
    assert AuditPermission().has_permission(_request(u), None) is True
    assert OperatorPermission().has_permission(_request(u), None) is False
    assert SuperuserPermission().has_permission(_request(u), None) is False


def test_operator_permission():
    u = _make_user(is_operator=True)
    assert OperatorPermission().has_permission(_request(u), None) is True
    assert AuditPermission().has_permission(_request(u), None) is False


def test_all_permission_authenticated():
    u = _make_user(is_authenticated=True)
    assert AllPermission().has_permission(_request(u), None) is True
