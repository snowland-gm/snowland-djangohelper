# -*- coding: utf-8 -*-
"""Tests for contrib apps (AppConfig correctness + model wiring).

These guard against two classes of regression:

1. AppConfig whose ``name`` does not match its Python module path — Django only
   detects this at ``apps.populate()`` time (e.g. ``Cannot import 'developer'``).
2. Model FKs hard-coded to ``AbstractUser`` (instead of ``settings.AUTH_USER_MODEL``)
   which fail to resolve under a swapped user model.

Both apps are loaded into ``INSTALLED_APPS`` in ``tests/test_settings.py`` with
MIGRATION_MODULES disabled, so Django builds their tables from the models.
"""
import importlib
import unittest

from django.apps import AppConfig, apps
from django.test import TestCase


class DeveloperAppConfigTest(unittest.TestCase):
    def test_config_resolves(self):
        cfg = apps.get_app_config('developer')
        self.assertIsInstance(cfg, AppConfig)

    def test_name_is_importable_module(self):
        # 复刻 Django apps.populate 的校验：name 必须是可导入的模块路径。
        # 原 bug：name='developer'（非可导入路径）会触发 ImportError。
        from djangohelper.contrib.developer.apps import DeveloperConfig
        mod = importlib.import_module(DeveloperConfig.name)
        self.assertEqual(mod.__name__, 'djangohelper.contrib.developer')
        self.assertEqual(DeveloperConfig.name.rsplit('.')[-1], 'developer')


class FriendLinkAppConfigTest(unittest.TestCase):
    def test_config_resolves(self):
        cfg = apps.get_app_config('friendlink')
        self.assertIsInstance(cfg, AppConfig)

    def test_name_is_importable_module(self):
        from djangohelper.contrib.friendlink.apps import FriendlinkConfig
        mod = importlib.import_module(FriendlinkConfig.name)
        self.assertEqual(mod.__name__, 'djangohelper.contrib.friendlink')
        self.assertEqual(FriendlinkConfig.label, 'friendlink')


class DeveloperModelTest(TestCase):
    def test_owner_fk_targets_swapped_user(self):
        # 关键回归点：owner 外键必须指向 settings.AUTH_USER_MODEL
        # （snowlandauth.SnowlandUser），而非硬编码的 AbstractUser。
        from django.conf import settings
        from djangohelper.contrib.developer.models import Application
        owner_field = Application._meta.get_field('owner')
        self.assertEqual(
            owner_field.related_model._meta.label,
            settings.AUTH_USER_MODEL,
        )

    def test_model_roundtrip(self):
        from djangohelper.contrib.developer.models import Application
        from djangohelper.contrib.snowlandauth.models import SnowlandUser
        user = SnowlandUser.objects.create(username='dev_owner', password='x')
        app = Application.objects.create(
            owner=user, name='app1', access_key='k', access_secret='s'
        )
        self.assertIsNotNone(app.pk)
        self.assertEqual(
            Application.objects.filter(owner=user).count(), 1
        )


class FriendLinkModelTest(TestCase):
    def test_model_roundtrip(self):
        from djangohelper.contrib.friendlink.models import FriendLink
        link = FriendLink.objects.create(
            site_name='example', url='https://example.com', date_start='2026-01-01'
        )
        self.assertIsNotNone(link.pk)
        self.assertTrue(link.show_flag)
        self.assertEqual(
            FriendLink.objects.filter(site_name='example').count(), 1
        )


if __name__ == '__main__':
    unittest.main()
