from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Account, Player, PlayerBoardStatus, BoardPosition, FencePosition

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Account.objects.all(),
                fields=['email', 'name'],
            )
        ]

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Player.objects.all(),
                fields=['id'],
            )
        ]

class PlayerBoardStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerBoardStatus
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=PlayerBoardStatus.objects.all(),
                fields=['id'],
            )
        ]

class BoardPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPosition
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=BoardPosition.objects.all(),
                fields=['id'],
            )
        ]

class FencePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FencePosition
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=FencePosition.objects.all(),
                fields=['id'],
            )
        ]