from django.test import TestCase
import time

from ..models import *
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class MyTurnTestCase1(APITestCase):
    def setUp(self):
        # Set up the initial data for testing
        GameStatus.objects.create(turn=1, round=1)
        account1 = Account.objects.create(email="abc@abc.com", name="홍길동", user_id="abc123", user_pw="1234")
        account2 = Account.objects.create(email="abc2@abc.com", name="홍길서", user_id="abc124", user_pw="1234")
        Player.objects.create(user_id=account1, remain_num=2)
        Player.objects.create(user_id=account2, remain_num=2)

    def test_my_turn(self):
        # 현재 아무도 선플레이어가 아님
        # 따라서 내 턴인지를 체크하면 False가 리턴되어야 한다.
        # Prepare the URL and query parameters
        url = 'http://3.36.7.233:3000/gamestatus/my_turn/'
        player_id = 1
        query_params = {'player_id': player_id}

        # Send a GET request to the URL with the query parameters
        response = self.client.get(url, query_params)

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        expected_result = {'my_turn': False}
        self.assertEqual(response.data, expected_result)

        # 플레이어1이 선플레이어가 됨
        # 따라서 내 턴인지를 체크하면 True가 리턴되어야 한다.
        player = Player.objects.get(id=1)
        player.fst_player = True
        player.save()

        # Send a GET request to the URL with the query parameters
        response = self.client.get(url, query_params)

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        expected_result = {'my_turn': True}
        self.assertEqual(response.data, expected_result)

        # 플레이어1이 행동을 하고 turn counter가 증가함
        # 따라서 플레이어2의 턴임
        # 따라서 플레이어1이 내 턴인지를 체크하면 False, 플레이어2가 체크하면 True가 리턴되어야 한다.
        gamestatus = GameStatus.objects.first()
        gamestatus.turn = 2
        gamestatus.save()

        # Player 1
        # Send a GET request to the URL with the query parameters
        response = self.client.get(url, query_params)

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        expected_result = {'my_turn': False}
        self.assertEqual(response.data, expected_result)

        # Player 2
        player_id = 2
        query_params = {'player_id': player_id}

        # Send a GET request to the URL with the query parameters
        response = self.client.get(url, query_params)

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        expected_result = {'my_turn': True}
        self.assertEqual(response.data, expected_result)

        # turn counter가 짝수지만 player 2의 남은 가족 구성원이 없는 경우
        # Player 1의 차례가 된다
        gamestatus.turn = 4
        gamestatus.save()
        player2 = Player.objects.get(id=2)
        player2.remain_num = 0
        player2.save()

        # Send a GET request to the URL with the query parameters
        player_id = 1
        query_params = {'player_id': player_id}
        response = self.client.get(url, query_params)

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the response data
        expected_result = {'my_turn': True}
        self.assertEqual(response.data, expected_result)