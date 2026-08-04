from django.db import models

from djangohelper.db.models import (
    BaseModel,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class TestArticle(BaseModel):
    """Concrete model used only by the test-suite to exercise BaseModel and viewsets."""
    __test__ = False  # tell pytest this is not a test class

    title = models.CharField(max_length=200)


class TestUUIDModel(UUIDMixin, models.Model):
    """Model exercising UUIDMixin only (keeps the default integer id)."""
    __test__ = False

    name = models.CharField(max_length=100)


class TestSoftDeleteModel(SoftDeleteMixin, models.Model):
    """Model exercising SoftDeleteMixin only (no timestamp, no uuid)."""
    __test__ = False

    name = models.CharField(max_length=100)


class TestFullModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Model composing all three mixins."""
    __test__ = False

    title = models.CharField(max_length=200)
