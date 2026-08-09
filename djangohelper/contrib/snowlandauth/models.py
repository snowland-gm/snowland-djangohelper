from django.contrib.auth.models import AbstractUser
from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)
from django.db import models
from django.db.models import Q
from enum import Enum

from djangohelper.contrib.snowlandauth.auth_mixins import (
    GenderMixin,
    PhoneMixin,
)


class TitleChoice(Enum):
    SUPERUSER = 0
    ADMIN = 1
    AUDIT = 2
    OPERATOR = 3


class SnowlandUser(PhoneMixin, GenderMixin, AbstractUser):
    """
    用户表
    """
    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    real_name = models.CharField(max_length=15, blank=True)


class OAuthAccount(models.Model):
    """A bound third-party OAuth account for a local user.

    Compose one of the provider mixins (``QQOAuthMixin``, ``WechatOAuthMixin``,
    ...) at subclass time, or use this base directly together with the
    ``provider`` field to store accounts from heterogeneous platforms in one
    table.
    """

    PROVIDER_CHOICES = (
        ('qq', 'QQ'),
        ('wechat', 'WeChat'),
        ('csdn', 'CSDN'),
        ('github', 'GitHub'),
        ('aliyun', 'Aliyun'),
        ('alipay', 'Alipay'),
        ('taobao', 'Taobao'),
    )

    user = models.ForeignKey(
        SnowlandUser,
        on_delete=models.CASCADE,
        related_name='oauth_accounts',
        verbose_name='关联用户',
    )
    provider = models.CharField(
        '授权平台',
        max_length=16,
        choices=PROVIDER_CHOICES,
    )
    openid = models.CharField(
        '第三方 OpenID',
        max_length=128,
        blank=True,
        db_index=True,
    )
    unionid = models.CharField(
        '第三方 UnionID',
        max_length=128,
        blank=True,
        default='',
        help_text='同一主体下跨应用统一标识（如微信开放平台）',
    )

    class Meta:
        verbose_name = '三方授权账户'
        verbose_name_plural = '三方授权账户'
        unique_together = (('provider', 'openid'),)

    def __str__(self):
        return '{}:{}'.format(self.provider, self.openid)


class AccountMergeRequest(PhoneMixin, models.Model):
    """A pending account-merge request generated when a logged-in user binds an
    OAuth identity that already belongs to *another* account.

    The user must choose which account to keep. After the choice is applied the
    affected user is forced to log in again (the original session is invalidated).
    """

    KEEP_CHOICES = (
        ('source', '保留当前登录账号'),
        ('target', '保留标识已绑定的账号'),
    )
    STATUS_CHOICES = (
        ('pending', '待用户选择'),
        ('done', '已合并'),
        ('cancelled', '已取消'),
    )

    user = models.ForeignKey(
        SnowlandUser,
        on_delete=models.CASCADE,
        related_name='merge_as_source',
        verbose_name='当前登录账号',
    )
    other_user = models.ForeignKey(
        SnowlandUser,
        on_delete=models.CASCADE,
        related_name='merge_as_target',
        verbose_name='标识已绑定的账号',
    )
    oauth_account = models.ForeignKey(
        OAuthAccount,
        on_delete=models.CASCADE,
        verbose_name='冲突的三方授权账户',
    )
    keep = models.CharField(
        '保留账号',
        max_length=8,
        choices=KEEP_CHOICES,
        blank=True,
        help_text='用户选择保留 source（当前登录）还是 target（标识已绑定）账号',
    )
    status = models.CharField(
        '状态',
        max_length=16,
        choices=STATUS_CHOICES,
        default='pending',
    )
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '账号合并请求'
        verbose_name_plural = '账号合并请求'

    def __str__(self):
        return 'merge#{}: {} <-> {}'.format(self.pk, self.user_id, self.other_user_id)


# https://blog.csdn.net/geerniya/article/details/78960812
class CustomBackend:
    """Password backend that also accepts a phone number (with optional
    country code) as the login identifier.

    It deliberately does *not* subclass ``ModelBackend`` at import time so the
    module can be loaded while the app registry is still populating (subclassing
    would trigger ``get_user_model()`` too early). The few ``ModelBackend``
    helpers we need are reused lazily.
    """

    def user_can_authenticate(self, user):
        from django.contrib.auth.backends import ModelBackend
        return ModelBackend().user_can_authenticate(user)

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        # 手机号登录：支持 "国家码+号码"（如 +8613800000000 / +86 138...）
        # 或纯号码（默认按中国大陆 +86 匹配）。
        phone_q = None
        if username.startswith('+'):
            # 形如 "+86 138..." 或 "+8613800000000"：拆出国家码与号码。
            for sep in (' ', '-'):
                if sep in username:
                    cc, _, num = username.partition(sep)
                    phone_q = Q(country_code=cc, telephone=num)
                    break
            if phone_q is None:
                # 没有分隔符，国家码最长 4 位（含 +），其余为号码。
                cc = username[:4] if len(username) > 4 else username
                phone_q = Q(country_code=cc, telephone=username[len(cc):])
        else:
            phone_q = Q(country_code=SnowlandUser.DEFAULT_COUNTRY_CODE, telephone=username)
        try:
            user = SnowlandUser.objects.get(
                Q(username=username) | Q(email=username) | phone_q
            )
        except ObjectDoesNotExist:
            # 故意走一次哈希计算，抹平"用户不存在"与"密码错误"的响应时间差，
            # 避免攻击者通过时序差异枚举已注册账号。
            SnowlandUser().set_password(password)
            return None
        except MultipleObjectsReturned:
            # 同一 telephone / email 命中多条记录属于数据异常，直接拒绝。
            return None
        if not self.user_can_authenticate(user):
            return None
        if user.check_password(password):
            return user
        return None
