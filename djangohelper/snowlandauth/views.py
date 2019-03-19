from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from djangohelper.snowlandauth.models import User


#
# https://blog.csdn.net/geerniya/article/details/78960812
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username) | Q(telephone=username))
            if user.check_password(password):
                return user
        except Exception as e:  # 可以捕获除与程序退出sys.exit()相关之外的所有异常
            return None
