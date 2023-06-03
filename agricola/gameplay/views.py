from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
from random import shuffle, choice
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .actions import *

# Create your views here.
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    @swagger_auto_schema(
    responses={
        200: openapi.Response(
            description='Success',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'first_player': openapi.Schema(type=openapi.TYPE_INTEGER),
                },
                required=['name'],
            ),
            examples={
                'application/json': {
                    'success' : True,
                    'first_player' : 1
                }
            }
        ),
    }
    )
    @action(detail=False, methods=['GET'])
    def choose_first_player(self, request):
        players = self.get_queryset()
        if players.exists():
            first_player = choice(players)
            players.update(fst_player=False)  # 모든 플레이어의 'fst_player' 필드를 False로 변경
            first_player.fst_player = True  # 선택된 선 플레이어의 'fst_player' 필드를 True로 설정
            first_player.save()
            return Response({'success': True, 'first_player': first_player.id})
        else:
            return Response({'success': False, 'message': 'No players found.'})

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

    @action(detail=False, methods=['get'])
    def get_random_jobcards(self, request):
        jobcards = list(JobCard.objects.all())
        shuffle(jobcards)  # 리스트를 랜덤하게 섞습니다.

        chunked_subcards = [jobcards[i:i + 7] for i in range(0, 14, 7)]  # 7개씩 두 묶음으로 나눕니다.
        serialized_data = []

        for chunk in chunked_subcards:
            serializer = JobCardSerializer(chunk, many=True)
            serialized_data.append(serializer.data)

        return Response(serialized_data)

class MainFacilityCardViewSet(ModelViewSet):
    queryset = MainFacilityCard.objects.all()
    serializer_class = MainFacilityCardSerializer

class ActionBoxViewSet(ModelViewSet):
    queryset = ActionBox.objects.all()
    serializer_class = ActionBoxSerializer

class GameStatusViewSet(ModelViewSet):
    queryset = GameStatus.objects.all()
    serializer_class = GameStatusSerializer

    @action(detail=False, methods=['get'])
    def get_turn(self, request):
        game_status = self.get_queryset().first()  # Assuming there is only one GameStatus instance
        turn_counter = game_status.turn
        return Response({'turn': turn_counter})


class FamilyPositionViewSet(ModelViewSet):
    queryset = FamilyPosition.objects.all()
    serializer_class = FamilyPositionSerializer

    @action(detail=False, methods=['post'])
    def take_action(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Load the player ID and action ID from the request data
        player_id = request.data.get('player_id')
        action_id = request.data.get('action_id')

        # Get the player and action objects
        player = Player.objects.get(id=player_id)
        another_player = Player.objects.exclude(id=player_id).first()
        action = ActionBox.objects.get(id=action_id)

        # Get the current turn counter from the game_status table
        game_status = GameStatus.objects.first()
        turn_counter = game_status.turn

        # Check whose turn it is based on the turn counter
        is_first_player_turn = turn_counter % 2 == 1

        # Check if it's the player's turn
        # 상대방의 가족 구성원이 없거나, 자신의 차례일 경우
        if another_player.remain_num == 0 or (is_first_player_turn and player.fst_player) or (not is_first_player_turn and not player.fst_player):
            # Action id 별로 메소드 호출

            # 덤불
            if action_id == 1:
                # perform_action_1()
                pass
            # 수풀
            elif action_id == 2:
                # perform_action_2()
                pass
            # 숲
            elif action_id == 11:
                response = forest(player)

            # 턴 카운터 업데이트
            game_status.turn = turn_counter + 1
            game_status.save()

            # FamilyPosition에 데이터 추가
            new_instance = FamilyPosition.objects.create(player_id=player, action_id=action, turn=turn_counter)
            new_instance.save()

            #가족 구성원 수 업데이트
            if player.remain_num != 0:
                player.remain_num -= 1
                player.save()

            return response
        else:
            return Response({'error': 'It is not your turn to take an action.'}, status=status.HTTP_403_FORBIDDEN)

class ResourceViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    
class PlayerResourceViewSet(ModelViewSet):
    queryset = PlayerResource.objects.all()
    serializer_class = PlayerResourceSerializer

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('resource_id', openapi.IN_QUERY, description='Resource ID', type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_player_resource(self, request):
        player_id = request.query_params.get('player_id')
        resource_id = request.query_params.get('resource_id')

        try:
            player_resource = PlayerResource.objects.get(player_id=player_id, resource_id=resource_id)
        except PlayerResource.DoesNotExist:
            return Response({'message': 'Player resource not found.'}, status=404)

        serializer = PlayerResourceSerializer(player_resource)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('resource_id', openapi.IN_QUERY, description='Resource ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('num_to_add', openapi.IN_QUERY, description='Number to add', type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def update_player_resource(self, request):
        player_id = request.query_params.get('player_id')
        resource_id = request.query_params.get('resource_id')
        num_to_add = int(request.query_params.get('num_to_add', 0))

        try:
            player_resource = PlayerResource.objects.get(player_id=player_id, resource_id=resource_id)
        except PlayerResource.DoesNotExist:
            return Response({'detail': 'Player resource not found.'}, status=404)

        resource_num = player_resource.resource_num + num_to_add

        if num_to_add < 0 and resource_num < 0:
            return Response({'detail': 'Cannot reduce resource below zero.'}, status=400)

        player_resource.resource_num = resource_num
        player_resource.save()

        serializer = PlayerResourceSerializer(player_resource)
        return Response(serializer.data)