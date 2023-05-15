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
