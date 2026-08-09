#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: oauth_mixins.py
# @Software: PyCharm

"""Model mixins for third-party OAuth authorization.

These mixins provide reusable field sets so concrete social-account models can
compose third-party OAuth bindings (QQ, WeChat, CSDN, GitHub, Aliyun, Alipay,
Taobao, ...) via multiple inheritance instead of duplicating field definitions.

Every OAuth mixin stores the platform-issued ``openid`` (the stable user
identifier on that platform) and declares ``oauth_type`` so callers can tell
which provider a row belongs to.

The **authorization-code callback flow** is delegated to the official
``snowland-authsdk`` package (:mod:`snowland_authsdk.oauth`). Each mixin binds a
platform client via the :attr:`SDK_CLIENT` class attribute (a subclass of
``snowland_authsdk.oauth.base.BaseOAuthClient``); ``get_authorize_url`` and
``resolve_identity`` are forwarded to the SDK client, which centralises endpoint
configuration and response parsing. Platforms not yet shipped as a ready-made
client in the SDK (QQ / Taobao) still subclass ``BaseOAuthClient`` here so they
share the same interface and behaviour.

Note: generic user-profile fields such as phone number and gender are *not*
part of OAuth and live in :mod:`djangohelper.contrib.snowlandauth.auth_mixins`
instead.
"""

import json
import re
from urllib.parse import parse_qs

from django.conf import settings
from django.db import models

from snowland_authsdk.oauth import (  # noqa: F401  (ensure SDK importable)
    AliyunOAuthClient,
    AlipayOAuthClient,
    CSDNOAuthClient,
    GitHubOAuthClient,
    WeChatOAuthClient,
)
from snowland_authsdk.oauth.base import BaseOAuthClient, OAuthError as SdkOAuthError


class OAuthMixin(models.Model):
    """Abstract base for third-party OAuth bindings.

    Concrete providers subclass this mixin and override :meth:`get_oauth_type`
    (or set the ``OAUTH_TYPE`` class attribute) to identify the platform. The
    ``openid`` column holds the stable user identifier issued by the provider.

    The OAuth callback is performed through :meth:`get_authorize_url` and
    :meth:`resolve_identity`. Subclasses set :attr:`SDK_CLIENT` to a
    ``snowland_authsdk.oauth.base.BaseOAuthClient`` subclass (see
    :class:`QQOAuthClient` / :class:`TaobaoOAuthClient` for platforms the SDK
    does not yet ship a ready-made client for).
    """

    #: Platform identifier returned by :meth:`get_oauth_type`.
    OAUTH_TYPE = 'unknown'

    #: ``snowland_authsdk`` client class for this platform. Every concrete
    #: provider mixin (including QQ / Taobao) must set this.
    SDK_CLIENT = None

    openid = models.CharField(
        '第三方 OpenID',
        max_length=128,
        blank=True,
        db_index=True,
        help_text='第三方平台下发的稳定用户标识',
    )

    class Meta:
        abstract = True

    @classmethod
    def get_oauth_type(cls):
        """Return the platform identifier for this OAuth mixin.

        :return: platform code string
        :rtype: str
        """
        return cls.OAUTH_TYPE

    @classmethod
    def _client_config(cls):
        """Read client id / secret / redirect uri from Django settings.

        The lookup key is the upper-cased :attr:`OAUTH_TYPE`, e.g. for ``qq``::

            SNOWLANDAUTH_OAUTH = {
                'QQ': {'CLIENT_ID': '...', 'CLIENT_SECRET': '...',
                       'REDIRECT_URI': 'https://example.com/oauth/callback'},
            }

        :return: dict with ``client_id``, ``client_secret`` and ``redirect_uri``
        :rtype: dict
        """
        conf = getattr(settings, 'SNOWLANDAUTH_OAUTH', {})
        return conf.get(cls.OAUTH_TYPE.upper(), {}) or {}

    @classmethod
    def get_sdk_client(cls):
        """Return an instantiated ``snowland_authsdk`` client, or ``None``.

        Only available when :attr:`SDK_CLIENT` is set for this platform.

        :return: SDK client instance or ``None``
        :rtype: BaseOAuthClient | None
        """
        if cls.SDK_CLIENT is None:
            return None
        cfg = cls._client_config()
        return cls.SDK_CLIENT(
            client_id=cfg.get('CLIENT_ID', ''),
            client_secret=cfg.get('CLIENT_SECRET', ''),
            redirect_uri=cfg.get('REDIRECT_URI', ''),
        )

    @classmethod
    def get_authorize_url(cls, state='', scope='', **extra):
        """Build the provider authorization URL the browser should be sent to.

        :param state: opaque CSRF state echoed back by the provider
        :type state: str
        :param scope: requested OAuth scope(s)
        :type scope: str
        :param extra: extra query params forwarded to the SDK client
        :return: fully qualified authorization URL
        :rtype: str
        :raises NotImplementedError: when no :attr:`SDK_CLIENT` is configured
        """
        client = cls.get_sdk_client()
        if client is None:
            raise NotImplementedError('{} 未配置 OAuth 客户端'.format(cls.__name__))
        url, _ = client.get_authorize_url(state=state or None, scope=scope)
        return url

    @classmethod
    def resolve_identity(cls, code, state='', **extra):
        """Run the callback for an authorization ``code`` and return the identity.

        The code is exchanged for an ``access_token`` via the SDK client, then
        (if the platform exposes a userinfo endpoint) the normalized user
        profile is read. When the platform has no userinfo endpoint the token's
        own openid is used.

        :param code: authorization code returned by the provider
        :type code: str
        :param state: CSRF state echoed by the provider (validated by caller)
        :type state: str
        :return: ``(openid, unionid, userinfo)`` where ``userinfo`` is a dict
        :rtype: tuple[str, str, dict]
        :raises RuntimeError: when the identity cannot be resolved
        """
        client = cls.get_sdk_client()
        if client is None:
            raise NotImplementedError('{} 未配置 OAuth 客户端'.format(cls.__name__))
        try:
            token = client.get_access_token(code, state=state, **extra)
        except SdkOAuthError as exc:
            raise RuntimeError('{} 授权失败: {}'.format(cls.OAUTH_TYPE, exc.message))
        openid = token.get('openid') or ''
        unionid = token.get('unionid') or ''
        if openid and getattr(client, 'USERINFO_URL', None):
            try:
                info = client.get_userinfo(
                    token.get('access_token'), openid=openid, **extra)
                openid = info.get('openid') or openid
                unionid = info.get('unionid') or unionid
                return openid, unionid, info
            except NotImplementedError:
                pass
        if not openid:
            raise RuntimeError('{} 返回数据缺少 openid'.format(cls.OAUTH_TYPE))
        return openid, unionid, token

    def __str__(self):
        return '{}(openid={})'.format(self.get_oauth_type(), self.openid)


class QQOAuthClient(BaseOAuthClient):
    """QQ Connect OAuth2 client built on the SDK base.

    QQ returns the token as a ``key=value`` query string and the openid via a
    separate JSONP ``me`` endpoint, so we override the two parse hooks.
    """

    AUTHORIZE_URL = 'https://graph.qq.com/oauth2.0/authorize'
    TOKEN_URL = 'https://graph.qq.com/oauth2.0/token'
    USERINFO_URL = 'https://graph.qq.com/oauth2.0/me'
    OPEN_ID_FIELD = 'openid'
    UNION_ID_FIELD = None

    def _token_response_parse(self, data):
        # QQ 的 token 接口返回 'access_token=...&expires_in=...' 文本。
        if isinstance(data, str):
            parsed = parse_qs(data)
            data = {k: v[0] for k, v in parsed.items()}
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_in': data.get('expires_in'),
            'openid': data.get('openid', ''),
            'raw': data,
        }

    def _userinfo_parse(self, data):
        # QQ 的 me 接口返回 callback( {"openid":"...","client_id":"..."} );
        if isinstance(data, str):
            match = re.search(r'\{.*\}', data, re.S)
            if not match:
                raise SdkOAuthError('无法解析 QQ openid 响应: {}'.format(data))
            data = json.loads(match.group(0))
        return {
            'openid': data.get('openid'),
            'unionid': data.get('unionid', ''),
            'raw': data,
        }


class TaobaoOAuthClient(BaseOAuthClient):
    """Taobao OAuth2 client built on the SDK base.

    Taobao has no standalone userinfo endpoint; the user id is returned together
    with the token, so :attr:`USERINFO_URL` is ``None`` and the openid is taken
    from the token response.
    """

    AUTHORIZE_URL = 'https://oauth.taobao.com/authorize'
    TOKEN_URL = 'https://oauth.taobao.com/token'
    USERINFO_URL = None
    OPEN_ID_FIELD = 'taobao_user_id'
    UNION_ID_FIELD = None

    def _token_response_parse(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except ValueError:
                parsed = parse_qs(data)
                data = {k: v[0] for k, v in parsed.items()}
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_in': data.get('expires_in'),
            'openid': data.get('taobao_user_id'),
            'unionid': data.get('taobao_user_id'),
            'nickname': data.get('taobao_user_nick'),
            'raw': data,
        }


class QQOAuthMixin(OAuthMixin):
    """QQ OAuth binding (openid issued by QQ Connect).

    Backed by :class:`QQOAuthClient`, a ``snowland_authsdk`` base subclass.
    """

    OAUTH_TYPE = 'qq'
    SDK_CLIENT = QQOAuthClient

    class Meta:
        abstract = True


class WechatOAuthMixin(OAuthMixin):
    """WeChat OAuth binding (openid issued by WeChat)."""

    OAUTH_TYPE = 'wechat'
    SDK_CLIENT = WeChatOAuthClient

    class Meta:
        abstract = True


class CSDNOAuthMixin(OAuthMixin):
    """CSDN OAuth binding (openid issued by CSDN)."""

    OAUTH_TYPE = 'csdn'
    SDK_CLIENT = CSDNOAuthClient

    class Meta:
        abstract = True


class GithubOAuthMixin(OAuthMixin):
    """GitHub OAuth binding (openid stores the GitHub node id / login)."""

    OAUTH_TYPE = 'github'
    SDK_CLIENT = GitHubOAuthClient

    class Meta:
        abstract = True


class AliyunOAuthMixin(OAuthMixin):
    """Aliyun (Alibaba Cloud) OAuth binding."""

    OAUTH_TYPE = 'aliyun'
    SDK_CLIENT = AliyunOAuthClient

    class Meta:
        abstract = True


class AlipayOAuthMixin(OAuthMixin):
    """Alipay OAuth binding (openid stores the Alipay user id)."""

    OAUTH_TYPE = 'alipay'
    SDK_CLIENT = AlipayOAuthClient

    class Meta:
        abstract = True


class TaobaoOAuthMixin(OAuthMixin):
    """Taobao OAuth binding (openid stores the Taobao user id).

    Backed by :class:`TaobaoOAuthClient`, a ``snowland_authsdk`` base subclass.
    """

    OAUTH_TYPE = 'taobao'
    SDK_CLIENT = TaobaoOAuthClient

    class Meta:
        abstract = True


__all__ = [
    'OAuthMixin',
    'QQOAuthClient',
    'TaobaoOAuthClient',
    'QQOAuthMixin',
    'WechatOAuthMixin',
    'CSDNOAuthMixin',
    'GithubOAuthMixin',
    'AliyunOAuthMixin',
    'AlipayOAuthMixin',
    'TaobaoOAuthMixin',
]
