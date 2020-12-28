from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from enum import Enum


class TitleChoice(Enum):
    SUPERUSER = 0
    ADMIN = 1
    AUDIT = 2
    OPERATOR = 3


class SnowlandUser(AbstractUser):
    """
    用户表
    """
    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    telephone = models.CharField(max_length=15, unique=True)
    sex = models.CharField(max_length=2, default='F')
    real_name = models.CharField(max_length=15, blank=True)


# https://blog.csdn.net/geerniya/article/details/78960812
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = SnowlandUser.objects.get(Q(username=username) | Q(email=username) | Q(telephone=username))
            if user.check_password(password):
                return user
        except Exception as e:  # 可以捕获除与程序退出sys.exit()相关之外的所有异常
            return None
