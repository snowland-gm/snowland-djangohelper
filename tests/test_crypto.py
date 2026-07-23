"""Tests for djangohelper.utils.crypto.pbkdf2."""
from djangohelper.utils.crypto import pbkdf2


def test_pbkdf2_returns_bytes():
    k = pbkdf2('pw', 'salt', 1000)
    assert isinstance(k, bytes)


def test_pbkdf2_deterministic():
    k1 = pbkdf2('pw', 'salt', 1000)
    k2 = pbkdf2('pw', 'salt', 1000)
    assert k1 == k2


def test_pbkdf2_salt_changes_output():
    k1 = pbkdf2('pw', 'salt', 1000)
    k3 = pbkdf2('pw', 'salt2', 1000)
    assert k1 != k3
