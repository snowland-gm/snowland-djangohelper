#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: mixins.py
# @Software: PyCharm

"""Reusable model mixins for Django models.

These mixins provide common database field patterns so concrete models can
compose them via multiple inheritance instead of duplicating field
definitions.
"""

import uuid as uuid_

from django.db import models


class UUIDMixin(models.Model):
    """Add a ``uuid`` field without touching the model's primary key.

    The model keeps its own ``id`` (e.g. the implicit ``AutoField``), while
    this mixin contributes an extra ``uuid`` column (defaulting to a random
    UUID) that can be used as an external/non-sequential identifier.
    """

    uuid = models.UUIDField(
        'UUID',
        default=uuid_.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """Add ``created_time`` and ``updated_time`` timestamp fields."""

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """Default manager returning only non-deleted rows."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class DeletedManager(models.Manager):
    """Manager returning only soft-deleted rows."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteMixin(models.Model):
    """Add a ``is_deleted`` flag and soft-delete behaviour.

    Calling ``instance.delete()`` only marks the row as deleted instead of
    removing it from the database. Use the ``active`` / ``deleted`` managers
    (or ``objects`` for the default including-deleted view) to filter rows.
    """

    is_deleted = models.BooleanField('是否删除', default=False, db_index=True)

    objects = models.Manager()
    active = ActiveManager()
    deleted = DeletedManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, soft=True):
        """Soft-delete by default.

        Pass ``soft=False`` to perform a real database deletion.
        """
        if soft:
            self.is_deleted = True
            self.save(using=using)
            return (1, {self.__class__.__name__: 1})
        return super().delete(using=using, keep_parents=keep_parents)

    def hard_delete(self, using=None, keep_parents=False):
        """Force a real deletion from the database."""
        return super().delete(using=using, keep_parents=keep_parents)


__all__ = [
    'UUIDMixin',
    'TimestampMixin',
    'SoftDeleteMixin',
    'ActiveManager',
    'DeletedManager',
]
