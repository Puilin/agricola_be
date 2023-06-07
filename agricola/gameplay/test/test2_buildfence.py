import time

from gameplay.models import *
from rest_framework import status
from rest_framework.test import APITestCase


class FenceBuilderTestCase(APITestCase):
    # 테스트에 필요한 초기 설정을 수행합니다.
    def setUp(self):
        # 임시 데이터베이스에 더미데이터 추가
        self.account = Account()
        self.account.email = "admin@google.com"
        self.account.user_id = "sys"
        self.account.user_pw = "sys"
        self.account.save()

        self.player = Player()
        self.player.user_id = self.account
        self.player.save()

        self.player_board_status = PlayerBoardStatus()
        self.player_board_status.player_id = self.player
        self.player_board_status.save()

        for i in range(1, 16): # 1~15
            self.board_position = BoardPosition()
            self.board_position.board_id = self.player_board_status
            self.board_position.position = i
            if i in [1, 2]:
                self.board_position.position_type = 1
                self.board_position.is_fam = True
            elif i in [11, 14]:
                self.board_position.position_type = 3
                self.board_position.is_fam = False
            else:
                self.board_position.position_type = 0
                self.board_position.is_fam = False
            self.board_position.save()

        self.board_id = BoardPosition.objects.get(position=11)
        self.fence_position = FencePosition()
        self.fence_position.position_id = self.board_id
        self.fence_position.left = True
        self.fence_position.right = True
        self.fence_position.top = True
        self.fence_position.bottom = False
        self.fence_position.save()

        self.board_id = BoardPosition.objects.get(position=14)
        self.fence_position = FencePosition()
        self.fence_position.position_id = self.board_id
        self.fence_position.left = True
        self.fence_position.right = True
        self.fence_position.top = False
        self.fence_position.bottom = True
        self.fence_position.save()

    def test_build_fence(self):

        # 테스트할 함수의 입력 데이터를 준비합니다.
        testcase = [{"player_id": 1, "fence_array": [[7, 8, 10]]},
                     {"player_id": 1, "fence_array": [[3, 6]]}]

        expected_result = [status.HTTP_200_OK,
                            status.HTTP_403_FORBIDDEN]

        # 테스트를 진행합니다.
        result = []
        execution_time = []

        for i in range(len(testcase)): # 2
            start_time = time.time() # 타이머 시작

            response = self.client.post('/fenceposition/build_fence/', data=testcase[i], format='json')
            result.append(response)

            end_time = time.time() # 타이머 종료
            execution_time.append(end_time - start_time)

        # 예상 결과와 실제 결과를 비교하여 검증합니다.
        print('[ 기존의 울타리가 있는 경우 ]')
        for i in range(len(testcase)):
            print(f'===== {i + 1}번째 테스트 실행 =====')
            print(f'입력 데이터: {testcase[i]}')
            # msg는 두 값이 같지 않을 때만 출력됩니다.
            self.assertEqual(result[i].status_code, expected_result[i], msg='테스트 실패')
            print(f"테스트 수행 시간: {execution_time[i]}초")
            print('\tSUCCESS!')