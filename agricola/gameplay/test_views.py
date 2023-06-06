from django.test import TestCase
import time
import os
import django
from django.urls import reverse
from gameplay.models import *
from rest_framework.response import Response
from rest_framework import status

class RoundEndTest(TestCase):
    def test_round_end(self):
        # GameStatus 객체를 생성합니다.
        game_status = GameStatus.objects.create(turn=5, round=3)

        # round_end 액션을 수행합니다.
        game_status.round_end()

        # 데이터베이스에서 업데이트된 GameStatus 객체를 가져옵니다.
        updated_game_status = GameStatus.objects.get(id=game_status.id)

        # round 값이 1 증가했는지 확인합니다.
        self.assertEqual(updated_game_status.round, 4)