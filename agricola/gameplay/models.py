from django.db import models

# Create your models here.
class Account(models.Model):
    email = models.CharField(primary_key=True, max_length=30, null=False, default='-')
    name = models.CharField(max_length=10)
    user_id = models.CharField(max_length=20, null=False)
    user_pw = models.CharField(max_length=20, null=False)

class Player(models.Model):
    # id = models.AutoField(primary_key=True) # primary_key 옵션이 없으면 자동으로 추가해준다
    user_id = models.ForeignKey('Account', on_delete=models.CASCADE)
    adult_num = models.IntegerField(null=False, default=2)
    baby_num = models.IntegerField(null=False, default=0)
    fst_player = models.BooleanField(default=False)
    score = models.IntegerField(null=False, default=0)

class PlayerBoardStatus(models.Model):
    player_id = models.ForeignKey('Player', on_delete=models.CASCADE)
    house = models.CharField(max_length=2, null=False, default="나무")
    room_num = models.IntegerField(null=False, default=2)

class BoardPosition(models.Model):
    board_id = models.ForeignKey('PlayerBoardStatus', on_delete=models.CASCADE)
    position = models.IntegerField(null=False)
    position_name = models.CharField(max_length=6, null=False, default='빈칸')
    is_fam = models.BooleanField(null=False, default=False)

class FencePosition(models.Model):
    board_id = models.ForeignKey('BoardPosition', on_delete=models.CASCADE)
    left = models.BooleanField(null=False, default=False)
    top = models.BooleanField(null=False, default=False)
    right = models.BooleanField(null=False, default=False)
    bottom = models.BooleanField(null=False, default=False)


class Account(models.Model):
    email = models.CharField(
        primary_key=True, max_length=30, null=False, default='-')
    name = models.CharField(max_length=10)
    user_id = models.CharField(max_length=20, null=False)
    user_pw = models.CharField(max_length=20, null=False)
