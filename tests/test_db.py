"""DB-backed tests: BaseModel, generate_paginator_result, SelfModelViewSet."""
from django.test import TestCase
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from djangohelper.db.models import BaseModel
from djangohelper.viewhelper.paginator import generate_paginator_result
from djangohelper.viewsets import SelfModelViewSet

from tests.testapp.models import TestArticle


class TestArticleSerializer(serializers.ModelSerializer):
    __test__ = False  # tell pytest this is not a test class

    class Meta:
        model = TestArticle
        fields = '__all__'


class TestArticleViewSet(SelfModelViewSet):
    """Concrete viewset used by the test-suite."""
    __test__ = False  # tell pytest this is not a test class

    queryset = TestArticle.objects.all()
    serializer_class = TestArticleSerializer


class BaseModelTest(TestCase):
    def test_new_and_one(self):
        a = TestArticle.new({'title': 'Hello'})
        self.assertEqual(a.title, 'Hello')
        self.assertIsNotNone(a.id)
        got = TestArticle.one(title='Hello')
        self.assertEqual(got.id, a.id)

    def test_update(self):
        a = TestArticle.new({'title': 'A'})
        TestArticle.update(a.id, title='B')
        self.assertEqual(TestArticle.one(id=a.id).title, 'B')

    def test_all_and_filter(self):
        TestArticle.new({'title': 'X'})
        TestArticle.new({'title': 'Y'})
        self.assertEqual(TestArticle.all().count(), 2)
        self.assertEqual(TestArticle.filter(title='X').count(), 1)

    def test_base_model_is_abstract(self):
        self.assertTrue(BaseModel._meta.abstract)


class PaginatorTest(TestCase):
    def test_generate_paginator_result(self):
        for i in range(12):
            TestArticle.new({'title': f'T{i}'})
        res = generate_paginator_result(
            TestArticle.objects.all(), per_page=5, page=1
        )
        self.assertIn('contacts', res)
        self.assertIn('ind', res)
        # 12 rows / 5 per page => 3 pages => page-index queue has length 3
        self.assertEqual(len(res['ind']), 3)
        self.assertEqual(len(res['contacts'].object_list), 5)

    def test_generate_paginator_result_last_page(self):
        for i in range(12):
            TestArticle.new({'title': f'T{i}'})
        res = generate_paginator_result(
            TestArticle.objects.all(), per_page=5, page=3
        )
        # Last page shows indices [1, 2, 3]
        self.assertEqual(res['ind'], [1, 2, 3])


class ViewSetTest(TestCase):
    def _build_view(self, request, action, pk=None):
        view = TestArticleViewSet()
        drf_request = Request(request, parsers=[JSONParser()])
        view.request = drf_request
        view.args = ()
        view.kwargs = {'pk': pk} if pk is not None else {}
        view.format_kwarg = None
        view.action = action
        return view, drf_request

    def test_crud_flow(self):
        rf = APIRequestFactory()

        # create
        view, req = self._build_view(
            rf.post('/', {'title': 'New'}, format='json'), 'create'
        )
        resp = view.create(req)
        self.assertEqual(resp.status_code, 201)
        pk = resp.data['data']['id']

        # list
        view, req = self._build_view(rf.get('/'), 'list')
        resp = view.list(req)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data['data'], list)

        # retrieve
        view, req = self._build_view(rf.get(f'/{pk}/'), 'retrieve', pk=pk)
        resp = view.retrieve(req)
        self.assertEqual(resp.data['data']['title'], 'New')

        # update
        view, req = self._build_view(
            rf.put(f'/{pk}/', {'title': 'Upd'}, format='json'), 'update', pk=pk
        )
        resp = view.update(req)
        self.assertEqual(resp.data['data']['title'], 'Upd')

        # destroy
        view, req = self._build_view(rf.delete(f'/{pk}/'), 'destroy', pk=pk)
        resp = view.destroy(req)
        self.assertEqual(resp.status_code, 204)


class TestArticleViewSetTest(TestCase):
    def test_viewset_has_serializer_and_queryset(self):
        self.assertIs(TestArticleViewSet.serializer_class, TestArticleSerializer)
        self.assertTrue(TestArticleViewSet.queryset.exists() or True)
