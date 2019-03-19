from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    """
    用户表
    """
    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    userid = models.CharField(max_length=32, primary_key=True, auto_created=True)
    QQ = models.CharField(max_length=32, default='123456', unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=15, unique=True)
    sex = models.CharField(max_length=1, default='F')
    realname = models.CharField(max_length=32, default=None)
    IDcard = models.CharField(max_length=19, default=None, null=True, blank=True, unique=True)


