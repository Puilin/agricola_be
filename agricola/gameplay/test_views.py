import sys
sys.path.append('C:/Users/sunmeng/agricola/be/agricola/gameplay')

from django.test import TestCase
import time
import os
import django

from models import *
from rest_framework.response import Response
from rest_framework import status


class FenceBuilderTestCase(TestCase):
    def setUp(self):
        # 테스트에 필요한 초기 설정을 수행합니다.
        os.environ['DJANGO_SETTINGS_MODULE'] = 'agricola.settings'
        django.setup()

        self.fence_position = FencePosition()

        # 임시 데이터베이스에 더미데이터 추가
        self.player_board_status = PlayerBoardStatus()
        self.player_board_status.player_id = 1
        self.player_board_status.save()

        for i in range(1, 16): # 1~15
            self.board_position = BoardPosition()
            self.board_position.board_id = self.player_board_status.id
            self.board_position.position = i
            if i in [1, 2]:
                self.board_position.position_type = 1
                self.board_position.is_fam = True
            else:
                self.board_position.position_type = 0
                self.board_position.is_fam = False
            self.board_position.save()

    def test_build_fence(self):

        # 테스트할 함수의 입력 데이터를 준비합니다.
        testcase = [{"player_id": 1, "fence_array": [[5, 6, 9], [8]]},
                    {"player_id": 1, "fence_array": [[2, 5, 8]]},
                    {"player_id": 1, "fence_array": [[13, 14, 8]]},
                    {"player_id": 1, "fence_array": [[4], [7], [10]]}]

        expected_result = [Response({"message": "fence update complete."}, status=status.HTTP_200_OK),
                           Response({'error': 'wrong position.'}, status=status.HTTP_403_FORBIDDEN),
                           Response({'error': 'wrong position.'}, status=status.HTTP_403_FORBIDDEN),
                           Response({"message": "fence update complete."}, status=status.HTTP_200_OK)]

        # 테스트를 진행합니다.
        result = []
        execution_time = []

        for i in range(len(testcase)): # 4
            start_time = time.time() # 타이머 시작

            result.append(self.fence_position.build_fence(testcase[i]))

            end_time = time.time() # 타이머 종료
            execution_time.append(end_time - start_time)

        # 예상 결과와 실제 결과를 비교하여 검증합니다.
        for i in range(testcase):
            print(f'===== {i}번째 테스트 실행 =====')
            print(f'입력 데이터: {testcase[0]}')
            # msg는 두 값이 같지 않을 때만 출력됩니다.
            self.assertEqual(result[i], expected_result[i], msg='테스트 실패')
            print(f"테스트 수행 시간: {execution_time[i]}초")

