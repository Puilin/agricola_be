from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
# Create your views here.
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class PlayerBoardStatusViewSet(ModelViewSet):
    queryset = PlayerBoardStatus.objects.all()
    serializer_class = PlayerBoardStatusSerializer

class BoardPositionViewSet(ModelViewSet):
    queryset = BoardPosition.objects.all()
    serializer_class = BoardPositionSerializer

class FencePositionViewSet(ModelViewSet):
    queryset = FencePosition.objects.all()
    serializer_class = FencePositionSerializer