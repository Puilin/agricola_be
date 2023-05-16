from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
from random import shuffle
from rest_framework.decorators import action
from rest_framework.response import Response
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

class PeriodCardViewSet(ModelViewSet):
    queryset = PeriodCard.objects.all()
    serializer_class = PeriodCardSerializer

class ActivationCostViewSet(ModelViewSet):
    queryset = ActivationCost.objects.all()
    serializer_class = ActivationCostSerializer

class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

class ResourceImgViewSet(ModelViewSet):
    queryset = ResourceImg.objects.all()
    serializer_class = ResourceImgSerialzier

class CardViewSet(ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer

class SubFacilityCardViewSet(ModelViewSet):
    queryset = SubFacilityCard.objects.all()
    serializer_class = SubFacilityCardSerializer
    @action(detail=False, methods=['get'])
    def get_random_subfacilitycards(self, request):
        subfacilitycards = list(SubFacilityCard.objects.all())
        shuffle(subfacilitycards)  # 리스트를 랜덤하게 섞습니다.

        chunked_subcards = [subfacilitycards[i:i+7] for i in range(0, 14, 7)]  # 7개씩 두 묶음으로 나눕니다.
        serialized_data = []

        for chunk in chunked_subcards:
            serializer = SubFacilityCardSerializer(chunk, many=True)
            serialized_data.append(serializer.data)

        return Response(serialized_data)

class JobCardViewSet(ModelViewSet):
    queryset = JobCard.objects.all()
    serializer_class = JobCardSerializer

class MainFacilityCardViewSet(ModelViewSet):
    queryset = MainFacilityCard.objects.all()
    serializer_class = MainFacilityCardSerializer

class ActionBoxViewSet(ModelViewSet):
    queryset = ActionBox.objects.all()
    serializer_class = ActionBoxSerializer
