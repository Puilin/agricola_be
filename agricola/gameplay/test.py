from django.test import TestCase
import time

from .models import *
from .views import GameStatusViewSet
from rest_framework import request

class FenceBuilderTestCase(TestCase):
    def setUp(self):
        # 테스트에 필요한 초기 설정을 수행합니다.
        self.fence_builder = FencePosition()

    def test_build_fence(self):
        # 타이머 시작
        start_time = time.time()

        # 테스트할 함수의 입력 데이터를 준비합니다.
        fence_array = [[5, 6, 9], [8]]

        # 함수를 호출합니다.
        result = self.fence_builder.build_fence(fence_array)

        # 예상 결과와 실제 결과를 비교하여 검증합니다.
        expected_result = "Fence built successfully"
        self.assertEqual(result, expected_result)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"테스트 수행 시간: {execution_time}초")

class MyTurnTestCase(TestCase):
    def setup(self):
        GameStatus.objects.create(turn=1, round=1)
        account = Account.objects.create(email="abc@abc.com", name="홍길동", user_id="abc123", user_pw="1234")
        Player.objects.create(user_id=account, remain_num=0)
    
    def test_my_turn(self):
        empty_request = request.Empty()
        result = GameStatusViewSet.my_turn(empty_request)
        self.assertEqual(result, False)