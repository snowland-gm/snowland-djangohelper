"""Tests for djangohelper.auth.hasher (SM3 based password hashers)."""
import pytest

from djangohelper.auth.hasher import (
    BCryptSM3PasswordHasher,
    PBKDF2_SM3PasswordHasher,
    SM3KDFPasswordHasher,
    SM3PasswordHasher,
    UnsaltedSM3PasswordHasher,
)


def test_sm3_encode_verify():
    h = SM3PasswordHasher()
    enc = h.encode('secret', 'saltsalt')
    assert enc.startswith('sm3$')
    assert h.verify('secret', enc) is True
    assert h.verify('wrong', enc) is False


def test_sm3_safe_summary():
    h = SM3PasswordHasher()
    enc = h.encode('secret', 'saltsalt')
    summary = h.safe_summary(enc)
    assert summary['algorithm'] == 'sm3'


def test_unsalted_sm3():
    h = UnsaltedSM3PasswordHasher()
    enc = h.encode('secret', '')
    assert enc.startswith('sm3$$')
    assert h.verify('secret', enc) is True
    assert h.verify('x', enc) is False


def test_pbkdf2_sm3():
    h = PBKDF2_SM3PasswordHasher()
    enc = h.encode('secret', 'saltsalt')
    assert enc.startswith('pbkdf2_sm3$')
    assert h.verify('secret', enc) is True
    assert h.verify('wrong', enc) is False
    assert h.must_update(h.encode('secret', 'saltsalt')) is False
    # harden_runtime should not raise
    h.harden_runtime('secret', enc)


def test_bcrypt_sm3():
    pytest.importorskip('bcrypt')
    h = BCryptSM3PasswordHasher()
    enc = h.encode('secret', h.salt())
    assert h.verify('secret', enc) is True
    assert h.verify('wrong', enc) is False


def test_sm3kdf_encode():
    h = SM3KDFPasswordHasher()
    enc = h.encode('secret', '')
    assert enc.startswith('sm3kdf$')
    assert h.verify('secret', enc) is True
    assert h.verify('wrong', enc) is False


def test_sm3kdf_bytes_and_summary():
    h = SM3KDFPasswordHasher()
    enc = h.encode(b'secret', '')
    assert h.verify(b'secret', enc) is True
    assert h.verify('secret', enc) is True
    summary = h.safe_summary(enc)
    assert summary['algorithm'] == 'sm3kdf'
    assert 'hash' in summary
