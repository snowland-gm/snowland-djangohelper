#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: __init__.py
# @Software: PyCharm

"""snowlandauth: third-party OAuth bindings and user profile extensions.

The two concerns are kept in separate submodules:

* :mod:`djangohelper.contrib.snowlandauth.oauth_mixins` -- third-party OAuth
  bindings (QQ, WeChat, CSDN, GitHub, Aliyun, Alipay, Taobao, ...).
* :mod:`djangohelper.contrib.snowlandauth.auth_mixins` -- generic, OAuth-free
  user-profile extensions (phone number, gender).

Registration / login and OAuth-binding flows live in
:mod:`djangohelper.contrib.snowlandauth.auth_flow` (framework-agnostic service
layer) and :mod:`djangohelper.contrib.snowlandauth.views` (DRF adapters).

The **OAuth authorization-code callback flow** is handled by the platform mixins
in :mod:`djangohelper.contrib.snowlandauth.oauth_mixins` together with
:func:`djangohelper.contrib.snowlandauth.auth_flow.exchange_oauth_code` (and
:func:`bind_oauth_code_for_authenticated_user` for an already logged-in user).
Each mixin binds a ``snowland_authsdk.oauth.base.BaseOAuthClient`` subclass
(e.g. :class:`QQOAuthClient` / :class:`TaobaoOAuthClient`) via its ``SDK_CLIENT``
attribute and exposes ``get_authorize_url`` / ``resolve_identity``; the client
id/secret/redirect uri are read from the ``SNOWLANDAUTH_OAUTH`` Django setting.

The DRF layer exposes ``OAuthAuthorizeView`` (returns the authorize URL) and
``OAuthCallbackView`` (receives the provider ``code`` and finishes login/bind).

Import what you need explicitly, e.g.::

    from djangohelper.contrib.snowlandauth.oauth_mixins import QQOAuthMixin
    from djangohelper.contrib.snowlandauth.auth_mixins import (
        PhoneMixin,
        GenderMixin,
    )
    from djangohelper.contrib.snowlandauth.auth_flow import (
        register_user,
        exchange_oauth_code,
    )

Models and admins live in :mod:`djangohelper.contrib.snowlandauth.models`.
"""
