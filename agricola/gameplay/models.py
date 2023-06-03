from django.db import models

# Create your models here.
class Account(models.Model):
    email = models.CharField(primary_key=True, max_length=30, null=False, default='-', unique=True)
    name = models.CharField(max_length=10)
    user_id = models.CharField(max_length=20, null=False, unique=True)
    user_pw = models.CharField(max_length=20, null=False)

class Player(models.Model):
    # id = models.AutoField(primary_key=True) # primary_key 옵션이 없으면 자동으로 추가해준다
    user_id = models.ForeignKey('Account', on_delete=models.CASCADE)
    adult_num = models.IntegerField(null=False, default=2)
    baby_num = models.IntegerField(null=False, default=0)
    fst_player = models.BooleanField(default=False)
    score = models.IntegerField(null=False, default=0)
    remain_num = models.IntegerField(null=True)

class PlayerBoardStatus(models.Model):
    player_id = models.ForeignKey('Player', on_delete=models.CASCADE)
    score = models.IntegerField(null=False, default=0)

class BoardPosition(models.Model):
    player_id = models.ForeignKey('PlayerBoardStatus', on_delete=models.CASCADE)
    position = models.IntegerField(null=False)
    position_name = models.CharField(max_length=6, null=False, default='빈칸')
    is_fam = models.BooleanField(null=False, default=False)
    vege_type = models.IntegerField(null=False, default=0)
    vege_num = models.IntegerField(null=False, default=0)
    house_type = models.IntegerField(null=False, default=0)
    house_num = models.IntegerField(null=False, default=0)
    cowshed_num = models.IntegerField(null=False, default=0)
    animal_type = models.IntegerField(null=False, default=0)

class FencePosition(models.Model):
    board_id = models.ForeignKey('BoardPosition', on_delete=models.CASCADE)
    left = models.BooleanField(null=False, default=False)
    top = models.BooleanField(null=False, default=False)
    right = models.BooleanField(null=False, default=False)
    bottom = models.BooleanField(null=False, default=False)

class Resource(models.Model):
    resource_name = models.CharField(max_length=4, null=False)

class PlayerResource(models.Model):
    player_id = models.ForeignKey('Player', on_delete=models.CASCADE)
    resource_id = models.ForeignKey('Resource', on_delete=models.CASCADE)
    resource_num = models.IntegerField(null=False, default=0)

class PeriodCard(models.Model):
    # id = models.AutoField(primary_key=True) # primary_key 옵션이 없으면 자동으로 추가해준다
    card_id = models.ForeignKey('Card', on_delete=models.CASCADE)
    period = models.IntegerField(null=False)

class ActivationCost(models.Model):
    card_id = models.ForeignKey('Card', on_delete=models.CASCADE)
    resource_id = models.ForeignKey('Resource', on_delete=models.CASCADE)
    resource_num = models.IntegerField(null=False)

class File(models.Model):
    path = models.CharField(null=False, max_length=255)
    filename = models.CharField(null=False, max_length=255)

class ResourceImg(models.Model):
    file_id = models.ForeignKey("File", on_delete=models.CASCADE)
    resource_id = models.ForeignKey("Resource", on_delete=models.CASCADE)

class Card(models.Model):
    cardname = models.CharField(max_length=20, null=False)
    card_img = models.ForeignKey('File', on_delete=models.CASCADE)

class SubFacilityCard(models.Model):
    card_id = models.ForeignKey('Card', on_delete=models.CASCADE)
    type = models.CharField(max_length=50)

class JobCard(models.Model):
    card_id = models.ForeignKey('Card', on_delete=models.CASCADE)
    type = models.CharField(max_length=50)

class MainFacilityCard(models.Model):
    card_id = models.ForeignKey('Card', on_delete=models.CASCADE)
    type = models.CharField(max_length=50)

class ActionBox(models.Model):
    card_id = models.ForeignKey('PeriodCard', null=True, on_delete=models.CASCADE)
    name = models.CharField(null=True, max_length=255)
    acc_resource = models.IntegerField(default=0)
    add_resource = models.IntegerField(default=0)
    round = models.IntegerField(null=False)
    is_res = models.BooleanField(default=False)
    is_occupied = models.BooleanField(null=False, default=False)

class FamilyPosition(models.Model):
    player_id = models.ForeignKey('Player', on_delete=models.CASCADE)
    action_id = models.ForeignKey('ActionBox', on_delete=models.CASCADE)
    turn = models.IntegerField(unique=True)

class GameStatus(models.Model):
    turn = models.IntegerField(default=1)
    round = models.IntegerField(null = False)