from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Account

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