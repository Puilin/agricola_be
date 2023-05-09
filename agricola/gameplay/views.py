from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
<<<<<<< HEAD
from .models import Account, Player, PlayerBoardStatus, BoardPosition, FencePosition
from .serializer import AccountSerializer, PlayerSerializer, PlayerBoardStatusSerializer, BoardPositionSerializer, FencePositionSerializer
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
=======
from .models import Account
from .serializer import AccountSerializer

# Create your views here.
# Create your views here.


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
>>>>>>> yh.hong
