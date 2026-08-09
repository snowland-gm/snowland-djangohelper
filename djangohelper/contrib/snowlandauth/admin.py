from django.contrib import admin

from djangohelper.contrib.snowlandauth.models import (
    AccountMergeRequest,
    OAuthAccount,
    SnowlandUser,
)


@admin.register(SnowlandUser)
class SnowlandUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'telephone', 'sex', 'real_name', 'is_staff')
    search_fields = ('username', 'telephone', 'real_name')


@admin.register(OAuthAccount)
class OAuthAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'openid', 'unionid')
    list_filter = ('provider',)
    search_fields = ('openid', 'unionid')


@admin.register(AccountMergeRequest)
class AccountMergeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'other_user', 'oauth_account', 'keep', 'status')
    list_filter = ('status', 'keep')
    search_fields = ('user__username', 'other_user__username')
