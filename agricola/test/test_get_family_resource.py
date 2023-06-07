# 테스트에 필요한 초기 세팅
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agricola.settings')
django.setup()
import unittest
from django.test import RequestFactory, TestCase
from gameplay.views import PlayerResourceViewSet


class PlayerResourceViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = PlayerResourceViewSet.as_view({'get': 'get_family_resource'})

    def test_get_family_resource(self):
        # query parameters로 request 생성
        query_params = {'player_id': 1, 'type': 'adult'}
        self.request = self.factory.get('/path/to/view/', data=query_params)

        # view의 get_family_resource를 call
        response = self.view(self.request)

        # 예상 결과와 실제 결과 비교
        expected_response = {'player_id': 1, 'adult': 2}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_get_family_resource_not_equal_query(self):
        # query parameters가 다른 경우
        query_params = {'player_id': 2, 'type': 'baby'}
        self.request = self.factory.get('/path/to/view/', data=query_params)
        response = self.view(self.request)
        expected_response = {'player_id': 2, 'baby': 0}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

    def test_get_family_resource_invalid_type(self):
        # invalid type인 경우
        query_params = {'player_id': 2, 'type': 'invalid'}
        self.request = self.factory.get('/path/to/view/', data=query_params)
        response = self.view(self.request)
        expected_response = {'message': 'Invalid type'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_response)

    def test_get_family_resource_invalid_player(self):
        # 존재하지 않는 player_id인 경우
        query_params = {'player_id': 999, 'type': 'adult'}
        self.request = self.factory.get('/path/to/view/', data=query_params)
        response = self.view(self.request)
        expected_response = {'message': 'Player not found.'}
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, expected_response)


if __name__ == '__main__':
    unittest.main()
