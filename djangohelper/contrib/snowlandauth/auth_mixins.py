#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: auth_mixins.py
# @Software: PyCharm

"""Generic user-profile extension mixins for the auth system.

These mixins are intentionally *independent* of third-party OAuth: they extend
a local user model with common profile fields (phone number, gender) that any
account may have regardless of how it authenticates. They live in a separate
module from :mod:`djangohelper.contrib.snowlandauth.oauth_mixins` so the two
concerns (OAuth binding vs. generic profile) stay decoupled.
"""

from django.db import models


class PhoneMixin(models.Model):
    """Add a phone number for SMS login / password recovery.

    The number is split into a ``country_code`` (defaults to ``'+86'``, i.e.
    mainland China) and the national ``telephone`` part. The pair is unique
    together so the same national number under different country codes does not
    collide. Use :meth:`set_phone` / :attr:`full_phone` to read or write the
    combined number.
    """

    #: ISO/ITU country calling code, e.g. ``'+86'``. Defaults to China (CN).
    DEFAULT_COUNTRY_CODE = '+86'

    country_code = models.CharField(
        '国家码',
        max_length=5,
        blank=True,
        default=DEFAULT_COUNTRY_CODE,
        help_text='手机号国家码，默认 +86（中国大陆）',
    )
    telephone = models.CharField(
        '手机号',
        max_length=15,
        blank=True,
        help_text='用于短信登录 / 找回密码的手机号码（不含国家码）',
    )

    class Meta:
        abstract = True
        unique_together = (('country_code', 'telephone'),)

    def set_phone(self, telephone, country_code=DEFAULT_COUNTRY_CODE):
        """Set the phone number, optionally overriding the country code.

        :param telephone: national number (without country code)
        :type telephone: str
        :param country_code: country calling code, defaults to ``'+86'``
        :type country_code: str
        """
        self.country_code = country_code or self.DEFAULT_COUNTRY_CODE
        self.telephone = (telephone or '').strip()

    @property
    def full_phone(self):
        """Return the combined ``country_code + telephone`` string.

        :return: e.g. ``'+8613800000000'``
        :rtype: str
        """
        code = self.country_code or self.DEFAULT_COUNTRY_CODE
        return '{}{}'.format(code, self.telephone or '')


class GenderMixin(models.Model):
    """Add a ``sex`` field with a common male / female choice set."""

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
    )

    sex = models.CharField(
        '性别',
        max_length=1,
        choices=GENDER_CHOICES,
        default='U',
    )

    class Meta:
        abstract = True


__all__ = [
    'PhoneMixin',
    'GenderMixin',
]
