from django.contrib.auth import models
from django.db.models.manager import EmptyManager


class User(models.AbstractUser):
    """
    用户表
    """
    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    email = models.EmailField('email address', blank=True, unique=True)
    QQ = models.CharField(max_length=32, default=None, unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=15, unique=True)
    sex = models.CharField(max_length=1, default='F')
    realname = models.CharField(max_length=32, default=None, null=True, blank=True)
    IDcard = models.CharField(max_length=19, default=None, null=True, blank=True, unique=True)
    registertime = models.DateTimeField(auto_now_add=True)
    integrals = models.IntegerField(default=0)
    vip = models.IntegerField(default=0)

    def __str__(self):
        return self.username

