from django.db import models

from djangohelper.db.models import BaseModel


class TestArticle(BaseModel):
    """Concrete model used only by the test-suite to exercise BaseModel and viewsets."""
    __test__ = False  # tell pytest this is not a test class

    title = models.CharField(max_length=200)
