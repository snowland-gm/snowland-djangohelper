#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: viewsets .py
# @time: 2021/1/9 17:52
# @Software: PyCharm

from django.http import Http404
from rest_framework import serializers
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from djangohelper.common import ERROR_CODE_RESOURCE_NOT_FOUND
from djangohelper.db.models import SoftDeleteMixin, UUIDMixin
from djangohelper.responses import APIResponse


def _build_model_serializer(model):
    """Dynamically build a ``ModelSerializer`` for ``model``.

    Used as a fallback when a viewset does not declare ``serializer_class``.

    Field adjustments based on model mixins:
    - ``UUIDMixin``: drop the internal ``id`` primary key from the output,
      keeping the external ``uuid`` only.
    - ``SoftDeleteMixin``: drop the ``is_deleted`` flag from the output.
    """
    exclude = []
    if issubclass(model, UUIDMixin):
        exclude.append('id')
    if issubclass(model, SoftDeleteMixin):
        exclude.append('is_deleted')

    if exclude:
        # When excluding fields, enumerate all concrete fields except the
        # excluded ones (DRF forbids combining ``fields='__all__'`` with
        # ``exclude``).
        field_names = [
            f.name for f in model._meta.get_fields()
            if f.name not in exclude and not f.many_to_many and not f.one_to_many
        ]
        meta_attrs = {'model': model, 'fields': field_names}
    else:
        meta_attrs = {'model': model, 'fields': '__all__'}
    meta = type('Meta', (), meta_attrs)
    return type(
        '{}Serializer'.format(model.__name__),
        (serializers.ModelSerializer,),
        {'Meta': meta},
    )


class SelfModelViewSet(ModelViewSet):
    def get_queryset(self):
        # Prefer an explicitly declared queryset; fall back to the model's
        # default manager.
        queryset = super().get_queryset()
        # Soft-delete models: hide logically deleted rows by default across
        # all actions that consume the queryset (list/retrieve/update...).
        if queryset is not None and issubclass(queryset.model, SoftDeleteMixin):
            queryset = queryset.filter(is_deleted=False)
        return queryset

    def get_serializer_class(self):
        # Prefer an explicitly declared serializer; fall back to a dynamically
        # generated ModelSerializer for the queryset's model.
        if getattr(self, 'serializer_class', None) is not None:
            return self.serializer_class
        return _build_model_serializer(self.get_queryset().model)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            # Covers both genuinely missing rows and soft-deleted rows that
            # have been filtered out by ``get_queryset``.
            return APIResponse(
                successful=False,
                code=ERROR_CODE_RESOURCE_NOT_FOUND,
                message='资源不存在',
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(instance)
        return APIResponse(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return APIResponse(data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponse(data=serializer.data)

    def perform_destroy(self, instance):
        # Soft-delete models: mark as deleted instead of removing the row.
        if isinstance(instance, SoftDeleteMixin):
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted'])
        else:
            instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Return the external identifier: ``uuid`` for UUIDMixin models,
        # otherwise the primary key ``id``.
        if isinstance(instance, UUIDMixin):
            key, value = 'uuid', instance.uuid
        else:
            key, value = 'id', instance.pk
        self.perform_destroy(instance)
        return APIResponse(data={key: value}, status=status.HTTP_200_OK)
