#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: views.py
# @Software: PyCharm

"""DRF views for registration / login and third-party OAuth binding.

These views are thin adapters around
:mod:`djangohelper.contrib.snowlandauth.auth_flow`. They translate HTTP
requests/responses into service-layer calls and return
:class:`djangohelper.responses.APIResponse`.
"""

from rest_framework import serializers, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated

from djangohelper.common import (
    ERROR_CODE_ACCOUNT_LOCKED_ERROR,
    ERROR_CODE_OPERATION_FAILED,
    ERROR_CODE_OPERATION_SUCCESS,
    ERROR_CODE_PARTNER_ERROR,
)
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
from djangohelper.contrib.snowlandauth.models import AccountMergeRequest
from djangohelper.responses import APIResponse


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    country_code = serializers.CharField(max_length=5, required=False, default='+86')
    telephone = serializers.CharField(max_length=15, required=False, default='')
    email = serializers.EmailField(required=False, default='')
    real_name = serializers.CharField(max_length=15, required=False, default='')


class PasswordLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class OAuthLoginSerializer(serializers.Serializer):
    provider = serializers.CharField()
    openid = serializers.CharField(required=False, default='')
    code = serializers.CharField(required=False, default='')
    state = serializers.CharField(required=False, default='')
    scope = serializers.CharField(required=False, default='')
    unionid = serializers.CharField(required=False, default='')
    country_code = serializers.CharField(max_length=5, required=False, default='+86')
    telephone = serializers.CharField(required=False, default='')
    email = serializers.EmailField(required=False, default='')
    real_name = serializers.CharField(required=False, default='')


class OAuthBindSerializer(serializers.Serializer):
    provider = serializers.CharField()
    openid = serializers.CharField()
    unionid = serializers.CharField(required=False, default='')


class MergeResolveSerializer(serializers.Serializer):
    merge_request_id = serializers.IntegerField()
    keep = serializers.ChoiceField(choices=['source', 'target'])


def _error(exc):
    """Build an APIResponse from an :class:`AuthFlowError`."""
    return APIResponse(
        successful=False,
        code=getattr(exc, 'code', ERROR_CODE_OPERATION_FAILED),
        message=exc.message,
        status=status.HTTP_400_BAD_REQUEST,
    )


class RegisterView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register_user(**serializer.validated_data)
        except AuthFlowError as exc:
            return _error(exc)
        return APIResponse(
            data={'id': user.id, 'username': user.username},
            code=ERROR_CODE_OPERATION_SUCCESS,
            message='注册成功',
            status=status.HTTP_201_CREATED,
        )


class PasswordLoginView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = login_by_password(
                request,
                serializer.validated_data['username'],
                serializer.validated_data['password'],
            )
        except AuthFlowError as exc:
            code = ERROR_CODE_ACCOUNT_LOCKED_ERROR if exc.code == 6 else ERROR_CODE_PARTNER_ERROR
            return APIResponse(
                successful=False,
                code=code,
                message=exc.message,
                status=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse(
            data={'id': user.id, 'username': user.username},
            code=ERROR_CODE_OPERATION_SUCCESS,
            message='登录成功',
        )


class OAuthLoginView(views.APIView):
    """Anonymous OAuth entry: login or auto-register, then start a session."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user, created = bind_or_login_oauth(
                request,
                provider=data['provider'],
                openid=data['openid'],
                unionid=data.get('unionid', ''),
                telephone=data.get('telephone', ''),
                country_code=data.get('country_code', ''),
                email=data.get('email', ''),
                real_name=data.get('real_name', ''),
            )
        except AuthFlowError as exc:
            code = ERROR_CODE_ACCOUNT_LOCKED_ERROR if exc.code == 6 else ERROR_CODE_PARTNER_ERROR
            return APIResponse(
                successful=False,
                code=code,
                message=exc.message,
                status=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse(
            data={'id': user.id, 'username': user.username, 'created': created},
            code=ERROR_CODE_OPERATION_SUCCESS,
            message='三方登录成功',
        )


class OAuthBindView(views.APIView):
    """Authenticated user binds a new OAuth provider.

    If the identity is already used by another account, the response carries
    ``merge_request_id`` and the client must call :class:`MergeResolveView`.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = OAuthBindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = bind_oauth_for_authenticated_user(
                request,
                request.user,
                provider=data['provider'],
                openid=data['openid'],
                unionid=data.get('unionid', ''),
            )
        except AuthFlowError as exc:
            return _error(exc)

        if result['status'] == 'merge_required':
            return APIResponse(
                data={'merge_request_id': result['merge_request_id']},
                code=ERROR_CODE_PARTNER_ERROR,
                message='该三方标识已绑定其他账号，请选择保留账号以完成合并',
                status=status.HTTP_409_CONFLICT,
            )
        return APIResponse(
            data={'bound': True},
            code=ERROR_CODE_OPERATION_SUCCESS,
            message='绑定成功',
        )


class MergeResolveView(views.APIView):
    """Resolve a pending account-merge request; forces re-login afterwards."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = MergeResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            kept = resolve_merge_request(
                request,
                data['merge_request_id'],
                data['keep'],
            )
        except AuthFlowError as exc:
            return _error(exc)
        except AccountMergeRequest.DoesNotExist:
            return APIResponse(
                successful=False,
                code=ERROR_CODE_PARTNER_ERROR,
                message='合并请求不存在',
                status=status.HTTP_404_NOT_FOUND,
            )
        return APIResponse(
            data={'kept_user_id': kept.id},
            code=ERROR_CODE_OPERATION_SUCCESS,
            message='合并完成，请重新登录',
        )


class OAuthAuthorizeView(views.APIView):
    """Return the provider authorization URL the client should redirect to.

    The client opens this URL in a browser; the provider then redirects back to
    the configured ``REDIRECT_URI`` (the :class:`OAuthCallbackView`).
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            client = get_oauth_client(data['provider'])
            url = client.get_authorize_url(
                state=data.get('state', ''),
                scope=data.get('scope', ''),
            )
        except (AuthFlowError, NotImplementedError) as exc:
            return _error(exc)
        return APIResponse(
            data={'authorize_url': url},
            code=ERROR_CODE_OPERATION_SUCCESS,
            message='请跳转到授权地址',
        )


class OAuthCallbackView(views.APIView):
    """OAuth redirect endpoint: receive ``code`` and finish login / binding.

    For an anonymous caller it logs in or auto-registers via
    :func:`exchange_oauth_code`. For an authenticated caller it binds the new
    identity (and may return ``merge_request_id`` for a conflict).
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        is_authed = bool(request.user and request.user.is_authenticated)
        try:
            if is_authed:
                result = bind_oauth_code_for_authenticated_user(
                    request,
                    request.user,
                    data['provider'],
                    data['code'],
                    state=data.get('state', ''),
                )
            else:
                user, created = exchange_oauth_code(
                    request,
                    data['provider'],
                    data['code'],
                    state=data.get('state', ''),
                    country_code=data.get('country_code', ''),
                    telephone=data.get('telephone', ''),
                    email=data.get('email', ''),
                    real_name=data.get('real_name', ''),
                )
        except (AuthFlowError, NotImplementedError, RuntimeError) as exc:
            code = ERROR_CODE_ACCOUNT_LOCKED_ERROR if getattr(exc, 'code', 0) == 6 else ERROR_CODE_PARTNER_ERROR
            return APIResponse(
                successful=False,
                code=code,
                message=str(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_authed:
            if result['status'] == 'merge_required':
                return APIResponse(
                    data={'merge_request_id': result['merge_request_id']},
                    code=ERROR_CODE_PARTNER_ERROR,
                    message='该三方标识已绑定其他账号，请选择保留账号以完成合并',
                    status=status.HTTP_409_CONFLICT,
                )
            return APIResponse(
                data={'bound': True},
                code=ERROR_CODE_OPERATION_SUCCESS,
                message='绑定成功',
            )

        return APIResponse(
            data={'id': user.id, 'username': user.username, 'created': created},
            code=ERROR_CODE_OPERATION_SUCCESS,
            message='三方登录成功',
        )
