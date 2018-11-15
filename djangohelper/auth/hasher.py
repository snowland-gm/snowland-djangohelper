#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: hasher.py
# @time: 2018/11/15 17:03
# @Software: PyCharm

from django.utils.translation import gettext_noop as _
from django.contrib.auth.hashers import BasePasswordHasher, OrderedDict, constant_time_compare, mask_hash, force_bytes


class SM3PasswordHasher(BasePasswordHasher):
    algorithm = 'sm3'
    library = ('SM3', 'pysmx.SM3')

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        SM3 = self._load_library()
        hash = SM3.Hash_sm3(force_bytes(salt + password))
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])


class UnsaltedSM3PasswordHasher(BasePasswordHasher):
    """
    Very insecure algorithm that you should *never* use; store SM3 hashes
    with an empty salt.

    This class is implemented because Django used to accept such password
    hashes. Some older Django installs still have these values lingering
    around so we need to handle and upgrade them properly.
    """
    algorithm = "unsalted_sm3"
    library = ('SM3', 'pysmx.SM3')

    def salt(self):
        return ''

    def encode(self, password, salt):
        assert salt == ''
        SM3 = self._load_library()
        hash = SM3.Hash_sm3(force_bytes(password))
        return 'sm3$$%s' % hash

    def verify(self, password, encoded):
        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        assert encoded.startswith('sm3$$')
        hash = encoded[6:]
        return OrderedDict([
            (_('algorithm'), self.algorithm),
            (_('hash'), mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        pass
