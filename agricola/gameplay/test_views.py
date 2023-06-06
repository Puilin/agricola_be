# unit test: get_family_resource

import os
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'agricola.settings'
settings.configure()

import sys
import unittest
from django.test import RequestFactory, TestCase

sys.path.append('/Users/hong_yehee/Desktop/django/be/agricola')
from agricola.gameplay.views import PlayerResourceViewSet

class PlayerResourceViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = PlayerResourceViewSet()

    def test_get_family_resource(self):
        # query parameters로 request 생성
        query_params = {'player_id': 1, 'type': 'adult'}
        request = self.factory.get('/path/to/view/', data=query_params)

        # view의 get_family_resource를 call
        response = self.view.get_family_resource(request)

        # 예상 결과와 실제 결과 비교
        expected_response = {'player_id': 1, 'adult': 5}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

        # query parameters가 다른 경우
        query_params = {'player_id': 2, 'type': 'baby'}
        request = self.factory.get('/path/to/view/', data=query_params)
        response = self.view.get_family_resource(request)
        expected_response = {'player_id': 2, 'baby': 3}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_response)

        # invalid type인 경우
        query_params = {'player_id': 3, 'type': 'invalid'}
        request = self.factory.get('/path/to/view/', data=query_params)
        response = self.view.get_family_resource(request)
        expected_response = {'message': 'Invalid type'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_response)

        # 존재하지 않는 player_id인 경우
        query_params = {'player_id': 999, 'type': 'adult'}
        request = self.factory.get('/path/to/view/', data=query_params)
        response = self.view.get_family_resource(request)
        expected_response = {'message': 'Player not found.'}
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, expected_response)

if __name__ == '__main__':
    unittest.main()
