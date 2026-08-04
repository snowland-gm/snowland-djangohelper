"""Tests for db.models mixins (UUIDMixin / TimestampMixin / SoftDeleteMixin)
and the SoftDelete-aware behaviours of SelfModelViewSet.
"""
import datetime

from django.test import TestCase
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from djangohelper.db.models import (
    ActiveManager,
    DeletedManager,
    SoftDeleteMixin,
    UUIDMixin,
    TimestampMixin,
)
from djangohelper.viewsets import SelfModelViewSet

from tests.testapp.models import (
    TestUUIDModel,
    TestSoftDeleteModel,
    TestFullModel,
)


# ---------------------------------------------------------------------------
# Mixin model definitions
# ---------------------------------------------------------------------------
class TestUUIDModelSerializer(serializers.ModelSerializer):
    __test__ = False

    class Meta:
        model = TestUUIDModel
        fields = '__all__'


class TestSoftDeleteModelSerializer(serializers.ModelSerializer):
    __test__ = False

    class Meta:
        model = TestSoftDeleteModel
        fields = '__all__'


class TestFullModelSerializer(serializers.ModelSerializer):
    __test__ = False

    class Meta:
        model = TestFullModel
        fields = '__all__'


class TestUUIDViewSet(SelfModelViewSet):
    __test__ = False
    queryset = TestUUIDModel.objects.all()
    serializer_class = TestUUIDModelSerializer


class TestSoftDeleteViewSet(SelfModelViewSet):
    __test__ = False
    queryset = TestSoftDeleteModel.objects.all()
    serializer_class = TestSoftDeleteModelSerializer


class TestFullViewSet(SelfModelViewSet):
    __test__ = False
    queryset = TestFullModel.objects.all()
    serializer_class = TestFullModelSerializer


# ---------------------------------------------------------------------------
# UUIDMixin
# ---------------------------------------------------------------------------
class UUIDMixinTest(TestCase):
    def test_uuid_field_added_not_pk(self):
        obj = TestUUIDModel.objects.create(name='a')
        # model keeps its own integer id as primary key
        self.assertIsNotNone(obj.id)
        self.assertEqual(obj._meta.pk.name, 'id')
        # uuid column is populated and unique
        self.assertIsNotNone(obj.uuid)
        self.assertTrue(UUIDMixin in type(obj).__mro__)

    def test_uuid_unique(self):
        obj1 = TestUUIDModel.objects.create(name='a')
        obj2 = TestUUIDModel.objects.create(name='b')
        self.assertNotEqual(obj1.uuid, obj2.uuid)

    def test_uuid_default_on_save(self):
        obj = TestUUIDModel(name='c')
        # default is applied on instantiation when not provided
        self.assertIsNotNone(obj.uuid)
        obj.save()
        self.assertIsNotNone(obj.uuid)


# ---------------------------------------------------------------------------
# TimestampMixin
# ---------------------------------------------------------------------------
class TimestampMixinTest(TestCase):
    def test_timestamps_populated(self):
        obj = TestFullModel.objects.create(title='t')
        self.assertIsNotNone(obj.created_time)
        self.assertIsNotNone(obj.updated_time)
        self.assertIsInstance(obj.created_time, datetime.datetime)
        # updated_time advances on save
        old = obj.updated_time
        obj.title = 't2'
        obj.save()
        self.assertGreaterEqual(obj.updated_time, old)

    def test_timestamp_fields_exist(self):
        self.assertTrue(hasattr(TestFullModel, 'created_time'))
        self.assertTrue(hasattr(TestFullModel, 'updated_time'))


# ---------------------------------------------------------------------------
# SoftDeleteMixin
# ---------------------------------------------------------------------------
class SoftDeleteMixinTest(TestCase):
    def test_default_not_deleted(self):
        obj = TestSoftDeleteModel.objects.create(name='a')
        self.assertFalse(obj.is_deleted)

    def test_soft_delete_marks_flag(self):
        obj = TestSoftDeleteModel.objects.create(name='a')
        obj.delete()  # soft by default
        obj.refresh_from_db()
        self.assertTrue(obj.is_deleted)
        # row still physically present
        self.assertEqual(
            TestSoftDeleteModel.objects.filter(pk=obj.pk).count(), 1
        )

    def test_hard_delete_removes_row(self):
        obj = TestSoftDeleteModel.objects.create(name='a')
        obj.delete(soft=False)
        self.assertEqual(
            TestSoftDeleteModel.objects.filter(pk=obj.pk).count(), 0
        )

    def test_active_and_deleted_managers(self):
        a = TestSoftDeleteModel.objects.create(name='a')
        b = TestSoftDeleteModel.objects.create(name='b')
        b.delete()
        self.assertIsInstance(TestSoftDeleteModel.active, ActiveManager)
        self.assertIsInstance(TestSoftDeleteModel.deleted, DeletedManager)
        self.assertEqual(TestSoftDeleteModel.active.count(), 1)
        self.assertEqual(TestSoftDeleteModel.deleted.count(), 1)
        self.assertIn(a, TestSoftDeleteModel.active.all())
        self.assertIn(b, TestSoftDeleteModel.deleted.all())

    def test_is_deleted_indexed(self):
        field = TestSoftDeleteModel._meta.get_field('is_deleted')
        self.assertTrue(field.db_index)


# ---------------------------------------------------------------------------
# SelfModelViewSet behaviour (soft-delete / uuid / dynamic serializer)
# ---------------------------------------------------------------------------
class _ViewHelper:
    """Build a minimally wired SelfModelViewSet instance for unit tests."""

    @staticmethod
    def build(viewset_cls, request, action, pk=None):
        view = viewset_cls()
        drf_request = Request(request, parsers=[JSONParser()])
        view.request = drf_request
        view.args = ()
        view.kwargs = {'pk': pk} if pk is not None else {}
        view.format_kwarg = None
        view.action = action
        return view


class ViewSetSoftDeleteTest(TestCase):
    def test_destroy_soft_delete_returns_id(self):
        rf = APIRequestFactory()
        obj = TestSoftDeleteModel.objects.create(name='a')

        view = _ViewHelper.build(
            TestSoftDeleteViewSet, rf.delete(f'/{obj.pk}/'), 'destroy', pk=obj.pk
        )
        resp = view.destroy(view.request)
        self.assertEqual(resp.status_code, 200)
        # no uuid mixin -> returns id
        self.assertEqual(resp.data['data'], {'id': obj.pk})

        obj.refresh_from_db()
        self.assertTrue(obj.is_deleted)
        # list hides soft-deleted rows
        view_list = _ViewHelper.build(TestSoftDeleteViewSet, rf.get('/'), 'list')
        list_resp = view_list.list(view_list.request)
        titles = [row['name'] for row in list_resp.data['data']]
        self.assertNotIn('a', titles)

    def test_retrieve_hidden_when_soft_deleted(self):
        rf = APIRequestFactory()
        obj = TestSoftDeleteModel.objects.create(name='a')
        obj.delete()

        view = _ViewHelper.build(
            TestSoftDeleteViewSet, rf.get(f'/{obj.pk}/'), 'retrieve', pk=obj.pk
        )
        resp = view.retrieve(view.request)
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(resp.data['successful'])


class ViewSetUUIDTest(TestCase):
    def test_destroy_returns_uuid_not_id(self):
        rf = APIRequestFactory()
        obj = TestUUIDModel.objects.create(name='a')

        view = _ViewHelper.build(
            TestUUIDViewSet, rf.delete(f'/{obj.pk}/'), 'destroy', pk=obj.pk
        )
        resp = view.destroy(view.request)
        self.assertEqual(resp.status_code, 200)
        # UUIDMixin -> returns uuid, not id
        self.assertIn('uuid', resp.data['data'])
        self.assertNotIn('id', resp.data['data'])
        self.assertEqual(str(resp.data['data']['uuid']), str(obj.uuid))
        # UUID model is not soft-deletable -> row truly removed
        self.assertEqual(
            TestUUIDModel.objects.filter(pk=obj.pk).count(), 0
        )


class DynamicSerializerTest(TestCase):
    """Exercise the fallback serializer (no explicit serializer_class)."""

    def test_fallback_excludes_id_for_uuid_model(self):
        class FallbackUUIDViewSet(SelfModelViewSet):
            __test__ = False
            queryset = TestUUIDModel.objects.all()

        ser_cls = FallbackUUIDViewSet().get_serializer_class()
        obj = TestUUIDModel.objects.create(name='a')
        data = ser_cls(obj).data
        self.assertIn('uuid', data)
        self.assertNotIn('id', data)

    def test_fallback_excludes_is_deleted_for_soft_model(self):
        class FallbackSoftViewSet(SelfModelViewSet):
            __test__ = False
            queryset = TestSoftDeleteModel.objects.all()

        ser_cls = FallbackSoftViewSet().get_serializer_class()
        obj = TestSoftDeleteModel.objects.create(name='a')
        data = ser_cls(obj).data
        self.assertIn('name', data)
        self.assertNotIn('is_deleted', data)

    def test_explicit_serializer_class_preferred(self):
        self.assertIs(
            TestFullViewSet().get_serializer_class(), TestFullModelSerializer
        )
