from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Account
from .serializer import AccountSerializer

# Create your views here.
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer