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

    def get_positionid(self, board_id, position):
        position_queryset = BoardPosition.objects.get(board_id=board_id, position=position)
        position_id = position_queryset.id
        return position_id

    def get_boardid_with_playerid(self, player_id):
        board_queryset = PlayerBoardStatus.objects.filter(player_id = player_id)
        board_id = board_queryset.first().id # 추후에 게임이 여러 개일 경우 어느 게임의 보드인지 구분 필요
        return board_id

    def get_fencepositions_with_boardid(self, board_id):
        positions = BoardPosition.objects.filter(board_id = board_id, position_type=3).values_list('position', flat=True)
        positions = list(positions)
        return positions # int 배열

    def get_invalid_position(self, board_id): # 집, 밭 포지션 가져오기
        position_query = BoardPosition.objects.filter(board_id=board_id, position_type=2).values_list('position', flat=True)
        positions = list(position_query)
        position_query = BoardPosition.objects.filter(board_id=board_id, position_type=1).values_list('position', flat=True)
        positions.extend(position_query)
        return positions

    def get_valid_position(self, ex_fence_list, invalid_position):  # fence_list에 있는 포지션들의 주변 포지션을 리턴
        if not ex_fence_list:  # 기존에 설치한 울타리가 없다면
            return list(range(1, 16))
        valid_position = []
        for position in ex_fence_list:
            if ((position % 3) != 0):  # 오른쪽 끝이 아니면
                valid_position.append(position + 1)
            if ((position % 3) != 1):  # 왼쪽 끝이 아니면
                valid_position.append(position - 1)
            if ((position + 3) < 16):  # 맨 밑이 아니면
                valid_position.append(position + 3)
            if ((position - 3) > 0):  # 맨 위가 아니면
                valid_position.append(position - 3)
        valid_position = list(set(valid_position) - set(ex_fence_list))
        valid_position = list(set(valid_position) - set(invalid_position))
        return valid_position

    def is_in_valid(self, fence_array, valid_position): # 울타리를 치고 싶은 포지션이 valid한지 검증
        for positions in fence_array:
            for position in positions:
                if position in valid_position:
                    return positions
        return False

    @action(detail=False, methods=['POST'])
    def build_fence(self, request): # { "player_id": 12, "fence_array": [[1, 2, 7], [6]] }
        player_id = request.data.get('player_id')
        board_id = self.get_boardid_with_playerid(player_id)

        fence_array = request.data.get('fence_array') # 추가하고 싶은 울타리들의 포지션 배열
        ex_fence_array = self.get_fencepositions_with_boardid(board_id) # 기존에 가지고 있던 울타리들의 포지션 배열
        invalid_position = self.get_invalid_position(board_id)  # 집, 밭 포지션
        valid_position = self.get_valid_position(ex_fence_array, invalid_position) # fence_array에 포함되어야 하는 포지션

        while (len(fence_array) > 0): # 유효한 울타리인지 검사
            new_position = self.is_in_valid(fence_array, valid_position)
            if new_position == False:
                return Response({'error': 'wrong position.'}, status=status.HTTP_403_FORBIDDEN)

            else:
                ex_fence_array.extend(new_position)
                valid_position = self.get_valid_position(ex_fence_array, invalid_position)
                fence_array = [sublist for sublist in fence_array if sublist != new_position]

        fence_array = request.data.get('fence_array')

        # db에 추가
        for fences in fence_array:
            fences = fences.sort()
            for i in range(len(fences)):
                left, right, top, bottom = [True, True, True, True]
                if (int(fences[i]) % 3 != 0) & ((int(fences[i]) + 1) in fences): # 오른쪽 끝 제외
                    right = False
                if (int(fences[i]) % 3 != 1) & ((int(fences[i]) - 1) in fences): # 왼쪽 끝 제외
                    left = False
                if (int(fences[i]) + 3 < 16) & ((int(fences[i]) + 3) in fences): # 맨 밑 제외
                    bottom = False
                if (int(fences[i]) - 3 > 0) & ((int(fences[i]) - 3) in fences): # 맨 위 제외
                    top = False

                # 해당 포지션의 type을 3으로 바꿈
                position_id = self.get_positionid(board_id, fences[i])
                board_position = BoardPosition.objects.get(id=position_id)
                board_position.position_type = 3
                board_position.save()

                # FencePosition 개체 생성 및 속성 설정
                fence_position = FencePosition()
                fence_position.position_id = position_id
                fence_position.left = left
                fence_position.right = right
                fence_position.top = top
                fence_position.bottom = bottom
                fence_position.save()

        return Response({"message": "fence update complete."}, status=status.HTTP_200_OK)
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

    @action(detail=False, methods=['post'])
    def get_mainfacility(self, request):
        return


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
    
    @action(detail=False, methods=['put'])
    def round_end(self, request):
        players = Player.objects.all()
        for player in players:
            player.remain_num = player.adult_num
            player.save()

        actionboxes = ActionBox.objects.all()
        for actionbox in actionboxes:
            if actionbox.is_res:
                actionbox.acc_resource += actionbox.add_resource
            else:
                actionbox.acc_resource = actionbox.add_resource
            actionbox.is_occupied = False
            actionbox.save()

        game_status = GameStatus.objects.all()
        game_status.round += 1
        game_status.turn = 1
        game_status.save()

    @action(detail=False, methods=['put'])
    def priod_end(self, request):
        players = Player.objects.all()
        for player in players:
            playerBoard = PlayerBoardStatus.objects.get(player_id = player.id)
            boardPositions = BoardPosition.objects.filter(player_id = playerBoard.player_id)
            # (수확1번) 1️⃣,2️⃣작물이 심어져 있는 밭에서 곡식/채소 1개씩 수확
            for boardPosition in boardPositions:
                if boardPosition.is_fam and boardPosition.vege_num != 0:
                    boardPosition.vege_num -= 1
                    playerResource = PlayerResource.objects.get(player_id=player.id, resource_id=boardPosition.vege_id)
                    playerResource.resource_num += 1
                    playerResource.save()
            # (수확2번) 1️⃣,2️⃣가족 먹여살리기
            playerfood = PlayerResource.objects.get(player_id=player.id, resource_id=10)
            consume = player.adult_num*2 + player.baby_num*2
            playerfood.resource_num -= consume
            hungrytoken = PlayerResource.objects.get(player_id=player.id, resource_id=11)
            while playerfood.resource_num < 0 :
                hungrytoken += 1
                playerfood += 1
            playerfood.save()
            hungrytoken.save()
            # (수확3번) 1️⃣,2️⃣동물 번식
            sheep = PlayerResource.objects.get(player_id=player.id, resource_id=7)
            if sheep.resource_num >= 2:
                sheep.resource_num += 1
            sheep.save()
            pig = PlayerResource.objects.get(player_id=player.id, resource_id=8)
            if pig.resource_num >= 2:
                pig.resource_num += 1
            pig.save()
            cow = PlayerResource.objects.get(player_id=player.id, resource_id=9)
            if cow.resource_num >= 2:
                cow.resource_num += 1
            cow.save()

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def my_turn(self, request):
        player_id = request.query_params.get('player_id')

        player = Player.objects.get(id=player_id)
        another_player = Player.objects.exclude(id=player_id).first()
        game_status = self.get_queryset().first()
        turn_counter = game_status.turn
        
        is_first_player_turn = turn_counter % 2 == 1
        
        result = another_player.remain_num == 0 or (is_first_player_turn and player.fst_player) or (not is_first_player_turn and not player.fst_player)

        return Response({'my_turn': result})
        

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
            #곡식종자
            elif action_id == 10:
                response = grain_seed(player)
            # 숲
            elif action_id == 11:
                response = forest(player)
            #집개조
            elif action_id == 21:
                response = house_upgrade(player)

            
            # 코드가 404면 -> 해당 행동이 거부됨 ->함수 종료
            if response.status_code == 404:
                return

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
            openapi.Parameter('resource_id', openapi.IN_QUERY, description='Resource ID', type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_player_resource(self, request):
        player_id = request.query_params.get('player_id')
        resource_id = request.query_params.get('resource_id')

        if resource_id == None:
            try:
                player_resources = PlayerResource.objects.filter(player_id=player_id)
            except PlayerResource.DoesNotExist:
                return Response({'message': 'Player resource not found.'}, status=404)
            serializer = PlayerResourceSerializer(player_resources, many=True)
            return Response(serializer.data)
        else:
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
            openapi.Parameter('type', openapi.IN_QUERY, description='adult or baby', type=openapi.TYPE_STRING, required=False),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_family_resource(self, request):
        player_id = request.query_params.get('player_id')
        type = request.query_params.get('type')

        try:
            player = Player.objects.get(id=player_id)
            adult = player.adult_num
            baby = player.baby_num
        except Player.DoesNotExist:
            return Response({'message': 'Player not found.'}, status=404)
        
        if type == None:
            return Response({'player_id':int(player_id), 'adult':adult, 'baby':baby})
        elif type == "adult":
            return Response({'player_id':int(player_id), 'adult':adult})
        elif type == 'baby':
            return Response({'player_id':int(player_id), 'baby':baby})
        else:
            return Response({'message': 'Invalid type'}, status=400)
    
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('type', openapi.IN_QUERY, description='cowshed or fence', type=openapi.TYPE_STRING, required=False),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_agricultural_resource(self, request):
        player_id = request.query_params.get('player_id')
        type = request.query_params.get('type')

        try:
            board = PlayerBoardStatus.objects.get(player_id=player_id)
            cowshed = board.cowshed_num
            fence = board.fence_num
        except PlayerBoardStatus.DoesNotExist:
            return Response({'message': 'Player not found.'}, status=404)
        
        if type == None:
            return Response({'player_id':int(player_id), 'cowshed':cowshed, 'fence':fence})
        elif type == "cowshed":
            return Response({'player_id':int(player_id), 'cowshed':cowshed})
        elif type == 'fence':
            return Response({'player_id':int(player_id), 'fence':fence})
        else:
            return Response({'message': 'Invalid type'}, status=400)

    @swagger_auto_schema(
        method='put',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'resource_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'num': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=False, methods=['put'])
    def update_player_resource(self, request):
        player_id = request.data.get('player_id')
        resource_id = request.data.get('resource_id')
        num_to_add = int(request.data.get('num', 0))

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

    @swagger_auto_schema(
        method='put',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'type': openapi.Schema(type=openapi.TYPE_STRING),
                'num': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=False, methods=['put'])
    def update_agricultural_resource(self, request):
        player_id = request.data.get('player_id')
        type = request.data.get('type')
        num = int(request.data.get('num'))

        if type == None:
            return Response({'message': 'Must specify type'}, status=400)
        if num == None:
            return Response({'message': 'Must specify num'}, status=400)
        
        try:
            board = PlayerBoardStatus.objects.get(player_id=player_id)
            cowshed = board.cowshed_num
            fence = board.fence_num

            if num < 0:
                if type == 'cowshed' and cowshed >= -num:
                    board.cowshed_num += num
                    board.save()
                    return Response({'player_id':int(player_id), 'cowshed':board.cowshed_num})
                elif type == 'fence' and fence >= -num:
                    board.fence_num += num
                    board.save()
                    return Response({'player_id':int(player_id), 'fence':board.fence_num})
                else:
                    return Response({'message': 'resource cannot be negative'}, status=400)
            else:
                if type == 'cowshed':
                    board.cowshed_num += num
                    board.save()
                    return Response({'player_id':int(player_id), 'cowshed':board.cowshed_num})
                elif type == 'fence':
                    board.fence_num += num
                    board.save()
                    return Response({'player_id':int(player_id), 'fence':board.fence_num})
        except PlayerBoardStatus.DoesNotExist:
            return Response({'message': 'PlayerBoardStatus not found.'}, status=404)
        
        