from django.test import TestCase
from gameplay.models import *
from rest_framework import status

class RoundEndTest(TestCase):
    def setUp(self):
        GameStatus.objects.create(round=1, turn=4)
        self.account1 = Account.objects.create(email="abc@abc.com", name="홍길동", user_id="abc123", user_pw="1234")
        Player.objects.create(user_id=self.account1, adult_num=2, baby_num=1, remain_num=0)
        self.account2 = Account.objects.create(email="abc1@abc.com", name="홍길서", user_id="123abc", user_pw="1234")
        Player.objects.create(user_id=self.account2, adult_num=3, baby_num=0, remain_num=0)
        # 숲
        forest_file = File.objects.create(id=1, path='/', filename='a')
        forest_card = Card.objects.create(id=10, card_img = forest_file)
        forest_pcard = PeriodCard.objects.create(card_id = forest_card, period = 0)
        ActionBox.objects.create(card_id=forest_pcard, name="숲", round=0, is_occupied=False, is_res=True, acc_resource=3, add_resource=3)
        # 곡식종자
        grain_file = File.objects.create(id=2, path='/', filename='a')
        grain_card = Card.objects.create(id=11, card_img = grain_file)
        grain_pcard = PeriodCard.objects.create(card_id = grain_card, period = 0)
        ActionBox.objects.create(card_id=grain_pcard, name="곡식종자", round=0, is_occupied=True, acc_resource=0, add_resource=1)

        
    def test_round_turn(self):
        url = 'http://3.36.7.233:3000/gamestatus/round_end/'
        
        response = self.client.put(url,{})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_result = {'next round':2, 'turn':1}

        data = response.data
        
        self.assertEqual(data['next round'], expected_result["next round"])
        self.assertEqual(data['turn'], expected_result["turn"])

    def test_player_board(self):
        url = 'http://3.36.7.233:3000/gamestatus/round_end/'
        response = self.client.put(url,{})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_result1 = {'adult_num':3,'baby_num':0,'remain_num':3}

        player1 = Player.objects.get(user_id=self.account1)
        self.assertEqual(player1.adult_num, expected_result1['adult_num'])
        self.assertEqual(player1.baby_num, expected_result1['baby_num'])
        self.assertEqual(player1.remain_num, expected_result1['remain_num'])

        expected_result2 = {'adult_num':3,'baby_num':0,'remain_num':3}
        player2 = Player.objects.get(user_id=self.account2)
        self.assertEqual(player2.adult_num, expected_result2['adult_num'])
        self.assertEqual(player2.baby_num, expected_result2['baby_num'])
        self.assertEqual(player2.remain_num, expected_result2['remain_num'])

    def test_actionbox(self):
        url = 'http://3.36.7.233:3000/gamestatus/round_end/'
        response = self.client.put(url,{})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_result_forest = {'acc_resource':6}
        expected_result_grain = {'acc_resource':1, 'is_occupied':False}

        result_forest = ActionBox.objects.get(name="숲")
        self.assertEqual(result_forest.acc_resource, expected_result_forest['acc_resource'])
        result_grain = ActionBox.objects.get(name="곡식종자")
        self.assertEqual(result_grain.acc_resource, expected_result_grain['acc_resource'])
        self.assertEqual(result_grain.is_occupied, expected_result_grain['is_occupied'])