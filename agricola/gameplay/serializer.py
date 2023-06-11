from rest_framework import serializers
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

class PeriodCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodCard
        fields = '__all__'

class ActivationCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivationCost
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class ResourceImgSerialzier(serializers.ModelSerializer):
    class Meta:
        model = ResourceImg
        fields = '__all__'

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

class SubFacilityCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubFacilityCard
        fields = '__all__'

class JobCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCard
        fields = '__all__'

class MainFacilityCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainFacilityCard
        fields = '__all__'

class ActionBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionBox
        fields = '__all__'

class FamilyPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyPosition
        fields = '__all__'

class GameStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameStatus
        fields = '__all__'

class PlayerResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerResource
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

class PlayerCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerCard
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class PenPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenPosition
        fields = '__all__'

class FstPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FstPlayer
        fields = '__all__'