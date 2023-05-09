from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import *


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class PlayerBoardStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerBoardStatus
        fields = '__all__'

class BoardPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPosition
        fields = '__all__'

class FencePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FencePosition
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class ResourceImgSerialzier(serializers.ModelSerializer):
    class Meta:
        model = ResourceImg
        fields = '__all__'