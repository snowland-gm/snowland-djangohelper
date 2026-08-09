#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: test_auth_flow.py
# @Software: PyCharm

"""Unit tests for the registration / login / OAuth-binding flows."""

import unittest
from unittest import mock

from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase

from djangohelper.contrib.snowlandauth.auth_flow import (
    AuthFlowError,
    bind_oauth_code_for_authenticated_user,
    bind_oauth_for_authenticated_user,
    bind_or_login_oauth,
    exchange_oauth_code,
    get_oauth_client,
    login_by_password,
    register_user,
    resolve_merge_request,
)
from djangohelper.contrib.snowlandauth.models import (
    AccountMergeRequest,
    OAuthAccount,
    SnowlandUser,
)
from djangohelper.contrib.snowlandauth.oauth_mixins import (
    QQOAuthClient,
    QQOAuthMixin,
    WechatOAuthMixin,
)
from snowland_authsdk.oauth import WeChatOAuthClient

User = SnowlandUser


def _request(path='/'):
    req = RequestFactory().post(path)
    req.session = SessionStore()
    return req


class RegisterFlowTest(TestCase):
    def test_register_creates_user(self):
        user = register_user('bob', 'pw123', telephone='13800000000')
        self.assertEqual(user.username, 'bob')
        self.assertTrue(User.objects.filter(username='bob').exists())

    def test_register_duplicate_username_raises(self):
        register_user('bob', 'pw123')
        with self.assertRaises(AuthFlowError):
            register_user('bob', 'other')


class PasswordLoginFlowTest(TestCase):
    def test_login_with_telephone(self):
        register_user('bob', 'pw123', telephone='13800000000')
        req = _request()
        # authenticate + login must not raise
        user = login_by_password(req, '13800000000', 'pw123')
        self.assertEqual(user.username, 'bob')

    def test_login_bad_password_raises(self):
        register_user('bob', 'pw123', telephone='13800000000')
        with self.assertRaises(AuthFlowError):
            login_by_password(_request(), '13800000000', 'wrong')

    def test_login_inactive_user_raises(self):
        user = register_user('bob', 'pw123')
        user.is_active = False
        user.save()
        with self.assertRaises(AuthFlowError):
            login_by_password(_request(), 'bob', 'pw123')


class OAuthAnonymousFlowTest(TestCase):
    def test_oauth_login_auto_registers(self):
        req = _request()
        user, created = bind_or_login_oauth(req, 'wechat', 'openid_wx_999')
        self.assertTrue(created)
        self.assertTrue(OAuthAccount.objects.filter(provider='wechat',
                                                    openid='openid_wx_999').exists())

    def test_oauth_login_existing_updates_unionid(self):
        req = _request()
        bind_or_login_oauth(req, 'wechat', 'openid_wx_999')
        req2 = _request()
        user, created = bind_or_login_oauth(req2, 'wechat', 'openid_wx_999',
                                            unionid='union_abc')
        self.assertFalse(created)
        self.assertEqual(user.oauth_accounts.first().unionid, 'union_abc')


class OAuthBindMergeFlowTest(TestCase):
    def test_bind_creates_account_when_free(self):
        user = register_user('alice', 'pw', telephone='13900000000')
        req = _request()
        req.user = user
        result = bind_oauth_for_authenticated_user(req, user, 'qq', 'qq_openid_1')
        self.assertEqual(result['status'], 'bound')
        self.assertTrue(OAuthAccount.objects.filter(user=user, provider='qq').exists())

    def test_bind_conflict_requires_merge(self):
        user_a = register_user('alice', 'pw', telephone='13900000000')
        user_b = register_user('ben', 'pw', telephone='13700000000')
        OAuthAccount.objects.create(user=user_b, provider='qq', openid='qq_shared')

        req = _request()
        req.user = user_a
        result = bind_oauth_for_authenticated_user(req, user_a, 'qq', 'qq_shared')
        self.assertEqual(result['status'], 'merge_required')
        self.assertTrue(AccountMergeRequest.objects.filter(pk=result['merge_request_id']).exists())

    def test_resolve_merge_keeps_source_and_deletes_target(self):
        user_a = register_user('alice', 'pw', telephone='13900000000')
        user_b = register_user('ben', 'pw', telephone='13700000000')
        oauth = OAuthAccount.objects.create(user=user_b, provider='qq', openid='qq_shared')

        req = _request()
        req.user = user_a
        result = bind_oauth_for_authenticated_user(req, user_a, 'qq', 'qq_shared')
        req_r = _request()
        req_r.user = user_a
        kept = resolve_merge_request(req_r, result['merge_request_id'], 'source')

        self.assertEqual(kept.username, 'alice')
        self.assertFalse(User.objects.filter(username='ben').exists())
        self.assertEqual(kept.oauth_accounts.get(provider='qq').openid, 'qq_shared')
        oauth.refresh_from_db()
        self.assertEqual(oauth.user_id, kept.id)

    def test_resolve_merge_keeps_target(self):
        user_a = register_user('alice', 'pw', telephone='13900000000')
        user_b = register_user('ben', 'pw', telephone='13700000000')
        OAuthAccount.objects.create(user=user_b, provider='qq', openid='qq_shared')

        req = _request()
        req.user = user_a
        result = bind_oauth_for_authenticated_user(req, user_a, 'qq', 'qq_shared')
        req_r = _request()
        req_r.user = user_a
        kept = resolve_merge_request(req_r, result['merge_request_id'], 'target')

        self.assertEqual(kept.username, 'ben')
        self.assertFalse(User.objects.filter(username='alice').exists())


class PhoneCountryCodeTest(TestCase):
    def test_default_country_code_is_cn(self):
        user = register_user('carol', 'pw', telephone='13600000000')
        self.assertEqual(user.country_code, '+86')
        self.assertEqual(user.full_phone, '+8613600000000')

    def test_override_country_code(self):
        user = register_user('dave', 'pw', telephone='2001234567', country_code='+1')
        self.assertEqual(user.country_code, '+1')
        self.assertEqual(user.full_phone, '+12001234567')

    def test_login_with_plain_telephone_defaults_to_cn(self):
        register_user('erin', 'pw', telephone='13500000000')
        req = _request()
        user = login_by_password(req, '13500000000', 'pw')
        self.assertEqual(user.username, 'erin')

    def test_login_with_explicit_country_code(self):
        register_user('frank', 'pw', telephone='2001234567', country_code='+1')
        req = _request()
        user = login_by_password(req, '+1 2001234567', 'pw')
        self.assertEqual(user.username, 'frank')


class OAuthCallbackFlowTest(TestCase):
    """Cover the authorization-code callback (code -> openid -> login/bind)."""

    def test_get_oauth_client_mapping(self):
        self.assertIs(get_oauth_client('qq'), QQOAuthMixin)
        self.assertIs(get_oauth_client('wechat'), WechatOAuthMixin)
        with self.assertRaises(AuthFlowError):
            get_oauth_client('unknown')

    def test_get_authorize_url_builds_query(self):
        url = WechatOAuthMixin.get_authorize_url(state='abc', scope='snsapi_userinfo')
        self.assertIn('open.weixin.qq.com', url)
        self.assertIn('state=abc', url)
        self.assertIn('scope=snsapi_userinfo', url)

    def test_exchange_oauth_code_auto_registers(self):
        # WeChat is backed by the snowland-authsdk client; mock the two SDK
        # calls (token exchange + userinfo) to avoid network IO.
        token = {'access_token': 'TOK', 'openid': 'wx_cb_1', 'unionid': 'u_1'}
        userinfo = {'openid': 'wx_cb_1', 'unionid': 'u_1', 'nickname': 'wxuser'}

        req = _request()
        with mock.patch.object(WeChatOAuthClient, 'get_access_token',
                               return_value=token), \
                mock.patch.object(WeChatOAuthClient, 'get_userinfo',
                                  return_value=userinfo):
            user, created = exchange_oauth_code(req, 'wechat', 'CODE123')
        self.assertTrue(created)
        oauth = OAuthAccount.objects.get(provider='wechat', openid='wx_cb_1')
        self.assertEqual(oauth.unionid, 'u_1')

    def test_bind_oauth_code_for_authenticated_user_conflict(self):
        user_a = register_user('alice', 'pw', telephone='13900000000')
        user_b = register_user('ben', 'pw', telephone='13700000000')
        OAuthAccount.objects.create(user=user_b, provider='qq', openid='qq_shared')

        token_json = {'access_token': 'T', 'openid': 'qq_shared'}
        req = _request()
        req.user = user_a
        with mock.patch.object(QQOAuthClient, 'get_access_token',
                               return_value=token_json):
            result = bind_oauth_code_for_authenticated_user(
                req, user_a, 'qq', 'CODE123')
        self.assertEqual(result['status'], 'merge_required')
        self.assertTrue(AccountMergeRequest.objects.filter(
            pk=result['merge_request_id']).exists())


if __name__ == '__main__':
    unittest.main()
