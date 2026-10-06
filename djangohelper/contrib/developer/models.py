from django.conf import settings
from django.db import models
from djangohelper.db.models import BaseModel


class Application(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    access_key = models.CharField(max_length=256)
    access_secret = models.CharField(max_length=256)
    icon = models.ImageField(null=True, blank=True)


class ApplicationChangeList(BaseModel):
    app_id = models.ForeignKey(Application, on_delete=models.CASCADE)
    access_key_before = models.CharField(max_length=256)
    access_key_after = models.CharField(max_length=256)
    access_secret_before = models.CharField(max_length=256)
    access_secret_after = models.CharField(max_length=256)


class KeyStore(BaseModel):
    app_id = models.ForeignKey(Application, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=256)
