#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: auth_flow.py
# @Software: PyCharm

"""Account registration / login and third-party OAuth binding flows.

This module holds the framework-agnostic business logic. The DRF views in
:mod:`djangohelper.contrib.snowlandauth.views` delegate to these helpers so the
rules stay testable without a request object.

OAuth binding rules
-------------------
* **Anonymous login (no session)**: after the provider callback returns the
  stable ``openid`` for ``provider``:
    - If a local user already owns that ``(provider, openid)`` -> update the
      binding (refresh ``unionid`` etc.) and log the user in.
    - Otherwise -> auto-create a local user, attach the binding, and log in.
* **Authenticated binding (a user is logged in)**: if the ``(provider, openid)``
  already belongs to *another* account, a merge is required. We create an
  :class:`AccountMergeRequest` and let the user pick which account to keep;
  after the merge the chosen account's owner must log in again.
"""

from django.contrib.auth import authenticate, login
from django.db import transaction

from djangohelper.contrib.snowlandauth.models import (
    AccountMergeRequest,
    OAuthAccount,
    SnowlandUser,
)
from djangohelper.contrib.snowlandauth.oauth_mixins import (
    AlipayOAuthMixin,
    AliyunOAuthMixin,
    CSDNOAuthMixin,
    GithubOAuthMixin,
    OAuthMixin,
    QQOAuthMixin,
    TaobaoOAuthMixin,
    WechatOAuthMixin,
)

#: Map a stored ``provider`` code to its OAuth client mixin so the callback
#: flow can resolve the platform endpoints and exchange ``code`` for an id.
_PROVIDER_CLIENTS = {
    'qq': QQOAuthMixin,
    'wechat': WechatOAuthMixin,
    'csdn': CSDNOAuthMixin,
    'github': GithubOAuthMixin,
    'aliyun': AliyunOAuthMixin,
    'alipay': AlipayOAuthMixin,
    'taobao': TaobaoOAuthMixin,
}


def get_oauth_client(provider):
    """Return the OAuth client mixin class for a ``provider`` code.

    :param provider: one of ``OAuthAccount.PROVIDER_CHOICES``
    :type provider: str
    :return: the matching mixin class
    :rtype: type
    :raises AuthFlowError: when the provider is unknown
    """
    client = _PROVIDER_CLIENTS.get(provider)
    if client is None:
        raise AuthFlowError('不支持的授权平台: {}'.format(provider), code=2)
    return client


class AuthFlowError(Exception):
    """Raised for expected, user-facing auth-flow failures."""

    def __init__(self, message, code=0):
        super().__init__(message)
        self.message = message
        self.code = code


def _normalize_openid(openid):
    """Coerce an OAuth identifier into a non-empty string.

    :param openid: raw identifier from the provider
    :type openid: str | None
    :return: stripped identifier
    :rtype: str
    :raises AuthFlowError: when the identifier is empty
    """
    if not openid:
        raise AuthFlowError('三方授权返回的唯一标识为空', code=2)
    return str(openid).strip()


def register_user(username, password, telephone='', country_code='', email='', **extra):
    """Register a brand-new local account.

    :param username: login name
    :type username: str
    :param password: plaintext password (stored hashed)
    :type password: str
    :param telephone: optional phone number (without country code)
    :type telephone: str
    :param country_code: optional country calling code, defaults to ``'+86'``
    :type country_code: str
    :param email: optional email
    :type email: str
    :param extra: extra ``SnowlandUser`` fields (e.g. ``real_name``, ``sex``)
    :return: created user instance
    :rtype: SnowlandUser
    :raises AuthFlowError: when the username already exists
    """
    if SnowlandUser.objects.filter(username=username).exists():
        raise AuthFlowError('用户名已存在', code=2)
    user = SnowlandUser(username=username, email=email or '')
    if telephone:
        user.set_phone(telephone, country_code=country_code or '')
    for key, value in extra.items():
        if hasattr(user, key):
            setattr(user, key, value)
    user.set_password(password)
    user.save()
    return user


def login_by_password(request, username, password):
    """Authenticate with username/email/telephone + password and start a session.

    :param request: the active HttpRequest (used to start the session)
    :param username: username, email or telephone
    :type username: str
    :param password: plaintext password
    :type password: str
    :return: authenticated user
    :rtype: SnowlandUser
    :raises AuthFlowError: on bad credentials or disabled account
    """
    user = authenticate(request, username=username, password=password)
    if user is None:
        raise AuthFlowError('用户名或密码错误', code=2)
    login(request, user)
    return user


@transaction.atomic
def bind_or_login_oauth(request, provider, openid, unionid='', telephone='',
                        country_code='', email='', real_name=''):
    """Login (or register) via a third-party OAuth identity.

    Use this for an *anonymous* (not yet logged-in) OAuth entry point. For a
    logged-in user binding a new provider, use
    :func:`bind_oauth_for_authenticated_user` instead.

    :param request: active HttpRequest
    :param provider: one of ``OAuthAccount.PROVIDER_CHOICES``
    :type provider: str
    :param openid: stable provider user identifier
    :type openid: str
    :param unionid: optional cross-app union id
    :type unionid: str
    :param telephone: used only when auto-registering a new user
    :type telephone: str
    :param country_code: optional country code for the new user's phone
    :type country_code: str
    :param email: used only when auto-registering a new user
    :type email: str
    :param real_name: used only when auto-registering a new user
    :type real_name: str
    :return: ``(user, created)`` where ``created`` is True for auto-register
    :rtype: tuple[SnowlandUser, bool]
    """
    openid = _normalize_openid(openid)

    existing = OAuthAccount.objects.filter(provider=provider, openid=openid).first()
    if existing is not None:
        # Already bound: refresh unionid and continue with the owner.
        if unionid and existing.unionid != unionid:
            existing.unionid = unionid
            existing.save(update_fields=['unionid'])
        user = existing.user
        if not user.is_active:
            raise AuthFlowError('该账号已被禁用', code=6)
        login(request, user)
        return user, False

    # Not bound yet: auto-register a local account and attach the binding.
    user = SnowlandUser(
        username='{}_{}'.format(provider, openid[-8:]),
        email=email or '',
        real_name=real_name or '',
    )
    if telephone:
        user.set_phone(telephone, country_code=country_code or '')
    user.set_unusable_password()
    user.save()
    OAuthAccount.objects.create(
        user=user,
        provider=provider,
        openid=openid,
        unionid=unionid or '',
    )
    login(request, user)
    return user, True


@transaction.atomic
def bind_oauth_for_authenticated_user(request, user, provider, openid, unionid=''):
    """Bind an OAuth identity to an already authenticated user.

    If the ``(provider, openid)`` already belongs to *another* account, a merge
    request is created and the caller must let the user decide which account to
    keep. The decision is applied via :func:`resolve_merge_request`.

    :param request: active HttpRequest
    :param user: the currently authenticated user
    :type user: SnowlandUser
    :param provider: one of ``OAuthAccount.PROVIDER_CHOICES``
    :type provider: str
    :param openid: stable provider user identifier
    :type openid: str
    :param unionid: optional cross-app union id
    :type unionid: str
    :return: a dict describing the outcome:
        ``{'status': 'bound'}`` on success, or
        ``{'status': 'merge_required', 'merge_request_id': <id>}`` when a
        conflicting identity was found on another account.
    :rtype: dict
    """
    openid = _normalize_openid(openid)

    conflict = OAuthAccount.objects.filter(provider=provider, openid=openid).first()
    if conflict is not None and conflict.user_id != user.id:
        # The identity belongs to another account -> require a merge decision.
        merge = AccountMergeRequest.objects.create(
            user=user,
            other_user=conflict.user,
            oauth_account=conflict,
            status='pending',
        )
        return {'status': 'merge_required', 'merge_request_id': merge.id}

    if conflict is not None and conflict.user_id == user.id:
        # Already bound to the current user: just refresh unionid.
        if unionid and conflict.unionid != unionid:
            conflict.unionid = unionid
            conflict.save(update_fields=['unionid'])
        return {'status': 'bound'}

    OAuthAccount.objects.create(
        user=user,
        provider=provider,
        openid=openid,
        unionid=unionid or '',
    )
    return {'status': 'bound'}


@transaction.atomic
def resolve_merge_request(request, merge_request_id, keep):
    """Apply a pending account-merge decision.

    The chosen account keeps its profile; the other account's OAuth bindings
    are moved onto the kept account (here we simply re-point the conflicting
    binding and delete the discarded account). After merging, the affected user
    must log in again, so any existing session is logged out.

    :param request: active HttpRequest (its session will be flushed)
    :param merge_request_id: id of the :class:`AccountMergeRequest`
    :type merge_request_id: int
    :param keep: ``'source'`` (keep current logged-in user) or
        ``'target'`` (keep the account that already owned the identity)
    :type keep: str
    :return: the kept user instance
    :rtype: SnowlandUser
    :raises AuthFlowError: on invalid ``keep`` value or already-resolved request
    """
    if keep not in ('source', 'target'):
        raise AuthFlowError('无效的保留账号选择', code=2)

    merge = AccountMergeRequest.objects.select_for_update().get(pk=merge_request_id)
    if merge.status != 'pending':
        raise AuthFlowError('该合并请求已处理', code=2)

    kept = merge.user if keep == 'source' else merge.other_user
    discarded = merge.other_user if keep == 'source' else merge.user

    # Re-point the conflicting OAuth binding onto the kept account.
    merge.oauth_account.user = kept
    merge.oauth_account.save(update_fields=['user'])

    # Move any other OAuth bindings from the discarded account.
    OAuthAccount.objects.filter(user=discarded).update(user=kept)

    # Persist the merge decision first; the discarded account is still
    # referenced by ``merge.other_user`` so we must finish the merge row
    # before deleting it (deleting first would make the FK "unsaved").
    merge.keep = keep
    merge.status = 'done'
    merge.save(update_fields=['keep', 'status'])

    # Discard the other account (hard delete is acceptable here because the
    # identity has been merged onto the kept account).
    discarded.delete()

    # Force the affected user to log in again: drop the current session.
    if request is not None and hasattr(request, 'session'):
        from django.contrib.auth import logout
        logout(request)

    return kept


def exchange_oauth_code(request, provider, code, state='', scope='', **profile):
    """Run the OAuth authorization-code callback and log in (or register).

    This is the *entry point that the provider redirects back to*. It:

    1. builds the platform client from ``provider``,
    2. exchanges the ``code`` for an ``access_token``,
    3. resolves the stable ``(openid, unionid)``,
    4. delegates to :func:`bind_or_login_oauth` for the actual login/register.

   Extra profile fields (``telephone``, ``email``, ``real_name``) are only used
    when a brand-new local account is auto-created.

    :param request: active HttpRequest
    :param provider: one of ``OAuthAccount.PROVIDER_CHOICES``
    :type provider: str
    :param code: authorization code returned by the provider
    :type code: str
    :param state: CSRF state echoed by the provider (validated by caller)
    :type state: str
    :param scope: requested OAuth scope(s)
    :type scope: str
    :param profile: optional profile fields for auto-registration
    :return: ``(user, created)`` where ``created`` is True for auto-register
    :rtype: tuple[SnowlandUser, bool]
    :raises AuthFlowError: on unknown provider, bad code, or disabled account
    """
    client = get_oauth_client(provider)
    openid, unionid, _userinfo = client.resolve_identity(code, state=state)
    return bind_or_login_oauth(
        request,
        provider=provider,
        openid=openid,
        unionid=unionid,
        telephone=profile.get('telephone', ''),
        country_code=profile.get('country_code', ''),
        email=profile.get('email', ''),
        real_name=profile.get('real_name', ''),
    )


@transaction.atomic
def bind_oauth_code_for_authenticated_user(request, user, provider, code, state=''):
    """OAuth authorization-code callback for an already authenticated user.

    Exchanges the ``code`` for an ``openid`` and delegates to
    :func:`bind_oauth_for_authenticated_user`, which handles the merge conflict
    when the identity already belongs to another account.

    :param request: active HttpRequest
    :param user: the currently authenticated user
    :type user: SnowlandUser
    :param provider: one of ``OAuthAccount.PROVIDER_CHOICES``
    :type provider: str
    :param code: authorization code returned by the provider
    :type code: str
    :param state: CSRF state echoed by the provider (validated by caller)
    :type state: str
    :return: outcome dict (see :func:`bind_oauth_for_authenticated_user`)
    :rtype: dict
    :raises AuthFlowError: on unknown provider or bad code
    """
    client = get_oauth_client(provider)
    openid, unionid, _userinfo = client.resolve_identity(code, state=state)
    return bind_oauth_for_authenticated_user(
        request,
        user,
        provider=provider,
        openid=openid,
        unionid=unionid,
    )
