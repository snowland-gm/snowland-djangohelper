"""Tests for djangohelper.number_tool."""
import string

from djangohelper.number_tool import random_hex_string, random_string


def test_random_string_length_and_charset():
    s = random_string(16)
    assert len(s) == 16
    assert all(c in string.ascii_letters + string.digits for c in s)


def test_random_string_default_length():
    s = random_string()
    assert len(s) == 32


def test_random_hex_string():
    s = random_hex_string(20)
    assert len(s) == 20
    assert all(c in '0123456789abcdef' for c in s)
