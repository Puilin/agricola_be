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
from .utils import *
import json
from django.db.models import Sum


# Create your views here.
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                'user_pw': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )
    @action(detail=False, methods=['POST'])
    def login(self, request):  # { 'user_id' : admin, 'user_pw': admin }
        input_id = request.data.get('user_id')
        input_pw = request.data.get('user_pw')

        try:
            # Account 테이블에서 id가 같은 객체 가져오기
            account = Account.objects.get(user_id=input_id)
        except Account.DoesNotExist:
            return Response({'message': 'Wrong ID.'}, status=status.HTTP_404_NOT_FOUND)

        if account.user_pw != input_pw:
            return Response({'message': 'Wrong Password.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Player 테이블에서 해당 계정이 갖고 있는 객체 가져오기
            player = Player.objects.get(user_id=account.email)
        except:
            return Response({'message': 'Player Not Exist.'}, status=status.HTTP_404_NOT_FOUND)

        player_id = player.id
        return Response({'message': 'Login Complete.', 'player_id': player_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def initial(self, request):
        players = Player.objects.all()
        for player in players:
            player.adult_num = 2
            player.baby_num = 0
            player.fst_player = False
            player.score = 0
            player.remain_num = 2
            player.save()
        boards = PlayerBoardStatus.objects.all()
        for board in boards:
            board.house_num = 2
            board.house_type = 0
            board.cowshed_num = 0
            board.fence_num = 0
            board.pen_num = 0
            board.save()
        gamestatus = GameStatus.objects.first()
        gamestatus.turn = 1
        gamestatus.round = 5
        gamestatus.save()
        pens = PenPosition.objects.all().delete()
        fences = FencePosition.objects.all().delete()
        position = BoardPosition.objects.all()
        for pos in position:
            if pos.position in [1, 2]:
                pos.position_type = 1
                pos.is_fam = True
            else:
                pos.position_type = 0
                pos.is_fam = False
            pos.vege_type = 0
            pos.vege_num = 0
            pos.animal_num = 0
            pos.save()
        playerresources = PlayerResource.objects.all()
        for pr in playerresources:
            if pr.resource_id_id in [1, 2, 3, 4]:
                pr.resource_num = 10
            elif pr.resource_id_id == 10:
                pr.resource_num = 2
            else:
                pr.resource_num = 0
            pr.save()
        playercards = PlayerCard.objects.all()
        for playercard in playercards:
            # 주요설비 카드 덱에서 제거
            if playercard.card_id.id in list(range(29, 39)):
                playercard.delete()
            playercard.activate = 0
            playercard.save()
        actionboxs = ActionBox.objects.all()
        for actionbox in actionboxs:
            if actionbox.is_res:
                actionbox.acc_resource = actionbox.add_resource
            actionbox.is_occupied = False
            actionbox.save()
        FamilyPosition.objects.all().delete()
        player_viewset = PlayerViewSet()
        player_viewset.choose_first_player(request)

        facility_cards = MainFacilityCard.objects.all()
        for facility_card in facility_cards:
            facility_card.player_id = 0
            facility_card.save()
        return Response(status=200)

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
                        'success': True,
                        'first_player': 1
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
            origin = FstPlayer.objects.first()
            origin.player_id = first_player.id
            origin.save()
            return Response({'success': True, 'first_player': first_player.id})
        else:
            return Response({'success': False, 'message': 'No players found.'})


class PlayerBoardStatusViewSet(ModelViewSet):
    queryset = PlayerBoardStatus.objects.all()
    serializer_class = PlayerBoardStatusSerializer

    # 어떤 플레이어의 점수를 계산해줄 것인지 player_id을 받는다
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
        ]
    )
    # 플레이어의 점수를 계산해주는 API
    @action(detail=False, methods=['GET'])
    def calculate_score(self, request):
        player_id = request.query_params.get('player_id')

        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response({'message': 'Player not found.'}, status=status.HTTP_404_NOT_FOUND)

        # 점수 넣는 변수 ('Player' model의 'score' field)
        player.score = 0

        board_positions = BoardPosition.objects.filter(board_id=player_id)
        for position in board_positions:
            position_type = position.position_type
            # 빈 칸 : 1개 당 -1점
            if position_type == 0:
                player.score -= 1
            # 울타리를 친 외양간 : 1개 당 1점
            if position_type == 5:
                player.score += 1

        # 밭
        field_count = board_positions.filter(board_id=player_id, position_type=2).count()
        if (field_count == 0 or field_count == 1):
            player.score -= 1
        elif (2 <= field_count <= 4):
            player.score += (field_count - 1)
        elif (field_count >= 5):
            player.score += 4

        # 우리 (칸 크기와 상관없이 울타리가 쳐져있는 영역의 수)
        player_board_status = PlayerBoardStatus.objects.filter(player_id=player_id)
        pen_num = 0
        for board_status in player_board_status:
            pen_num += board_status.pen_num
        if pen_num == 0:
            player.score -= 1
        elif (1 <= pen_num <= 3):
            player.score += pen_num
        elif pen_num >= 4:
            player.score += 4

        for house_num in player_board_status:
            house_type = house_num.house_type
            # 흙집 : 1개 당 1점
            if house_type == 1:
                player.score += 1
            # 돌집 : 1개 당 2점
            elif house_type == 2:
                player.score += 2

        # 가족 말 : 1개 당 3점
        total_fam_num = player.adult_num + player.baby_num
        player.score += (total_fam_num * 3)

        # 구걸 토큰 : 1개 당 -3점
        player_resource = PlayerResource.objects.filter(player_id=player_id, resource_id=11)
        for resource in player_resource:
            player.score += resource.resource_num * (-3)

        # 양
        sheep_resource = PlayerResource.objects.filter(player_id=player_id, resource_id=7)
        sheep_count = sheep_resource.aggregate(total_sheep=Sum('resource_num'))['total_sheep']
        if (sheep_count == 0):
            player.score -= 1
        elif (1 <= sheep_count <= 3):
            player.score += 1
        elif (4 <= sheep_count <= 5):
            player.score += 2
        elif (6 <= sheep_count <= 7):
            player.score += 3
        elif (sheep_count >= 8):
            player.score += 4

        # 돼지
        pig_resource = PlayerResource.objects.filter(player_id=player_id, resource_id=8)
        pig_count = pig_resource.aggregate(total_pig=Sum('resource_num'))['total_pig']
        if (pig_count == 0):
            player.score -= 1
        elif (1 <= pig_count <= 2):
            player.score += 1
        elif (3 <= pig_count <= 4):
            player.score += 2
        elif (5 <= pig_count <= 6):
            player.score += 3
        elif (pig_count >= 7):
            player.score += 4

        # 소
        cow_resource = PlayerResource.objects.filter(player_id=player_id, resource_id=9)
        cow_count = cow_resource.aggregate(total_cow=Sum('resource_num'))['total_cow']
        if (cow_count == 0):
            player.score -= 1
        elif (cow_count == 1):
            player.score += 1
        elif (2 <= cow_count <= 3):
            player.score += 2
        elif (4 <= cow_count <= 5):
            player.score += 3
        elif (cow_count >= 6):
            player.score += 4

        # 곡식 (밭 위) 개수 구하기
        board_positions = BoardPosition.objects.filter(board_id__player_id=player_id, vege_type=1)
        crop_count = board_positions.count()
        # 곡식 (개인자원판) 개수 구하기
        player_resources = PlayerResource.objects.filter(player_id=player_id, resource_id=5)
        crop_count += player_resources.count()
        # 곡식 점수 계산
        if (crop_count == 0):
            player.score -= 1
        elif (1 <= crop_count <= 3):
            player.score += 1
        elif (4 <= crop_count <= 5):
            player.score += 2
        elif (6 <= crop_count <= 7):
            player.score += 3
        elif (crop_count >= 8):
            player.score += 4

        # 채소 (밭 위) 개수 구하기
        board_positions = BoardPosition.objects.filter(board_id__player_id=player_id, vege_type=2)
        vege_count = board_positions.count()
        # 채소 (개인자원판) 개수 구하기
        player_resources = PlayerResource.objects.filter(player_id=player_id, resource_id=6)
        vege_count += player_resources.count()
        # 채소 점수 계산
        if (vege_count == 0):
            player.score -= 1
        elif (1 <= vege_count <= 4):
            player.score += vege_count

        # 카드 점수 (활성화 된 상태여야 함)
        player_card = PlayerCard.objects.filter(player_id=player_id, activate=1)
        for card_num in player_card:
            card_id_str = str(card_num.card_id)
            card_id = int(card_id_str.split(" ")[2][1:-1])

            if (card_id == 16):
                player.score += 1
            if (card_id == 19):
                player.score += 1
            if (card_id == 21):
                player.score += 1
            if (card_id == 24):
                player.score += 1
            if (card_id == 26):
                player.score += 1
            if (card_id == 28):
                player.score += 2

        player.save()

        return Response({'player_id': player_id, 'score': player.score})

    @swagger_auto_schema(
        method='put',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.TYPE_INTEGER,
                'animal_type': openapi.TYPE_INTEGER,
                'position': openapi.TYPE_INTEGER
            }
        )
    )
    @action(detail=False, methods=['PUT'])
    def raise_animal(self, request):
        player_id = request.data.get('player_id')
        animal_type = request.data.get('animal_type')
        position = request.data.get('position')

        player = Player.objects.get(id=player_id)
        board = self.queryset.get(player_id=player)
        slot = BoardPosition.objects.filter(board_id=board).get(position=position)  # 칸번호로 포지션 받아오기
        if slot is None:
            return Response({'error': 'Invalid Position'}, status=403)
        resouce = PlayerResource.objects.filter(player_id=player).get(resource_id=animal_type + 6)
        if resouce is None:
            return Response({'error': 'Invalid animal_type'}, status=403)
        position_type = slot.position_type
        # 우리가 아님
        if position_type in [0, 1, 2]:
            return Response({'error': 'that position is not pen'}, status=403)

        # 해당 칸에 동물이 아무도 없으면
        if slot.animal_num == 0:
            if (get_animal_type(board, position) == 0):
                if (update_animal_type(board, position, animal_type)):
                    pass
                else:
                    return Response({'error': 'update_animal_type'}, status=500)
            slot.animal_num += 1
            slot.save()
            pen = get_pen_by_postiion(board, position)
            if pen is None: # 외양간 하나임
                pass
            else:
                pen.current_num += 1
                pen.save()
            resouce.resource_num -= 1
            resouce.save()
            return Response({'message': 'succeessfully added a(an) {} to {}'.format(animal_type, position)})
        else:
            max_num = 0
            if position_type == 3:  # 울타리 -> 최대 2마리
                max_num = 2
            elif position_type == 4:  # 외양간 -> 최대 1마리
                max_num = 1
            elif position_type == 5:  # 울타리외양간 -> 최대 4마리
                max_num = 4
            if slot.animal_num == max_num:
                return Response({'error': 'That slot has maximum number of animals.'}, status=403)
            # 우리의 가축 종류와 요청한 가축 종류가 같지 않다면
            if animal_type != get_animal_type(board, position):
                return Response({'error': 'Only the same type of animal can be put here.'}, status=403)
            slot.animal_num += 1
            slot.save()
            pen = get_pen_by_postiion(board, position) # 외양간은 이 코드에 도달할 일이 없음
            pen.current_num += 1
            pen.save()
            resouce.resource_num -= 1
            resouce.save()
            return Response({'message': 'succeessfully added a(an) {} to {}'.format(animal_type, position)})


class BoardPositionViewSet(ModelViewSet):
    queryset = BoardPosition.objects.all()
    serializer_class = BoardPositionSerializer

    @swagger_auto_schema(
        method='put',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'land_num': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=False, methods=['PUT'])
    def construct_land(self, request):
        player_id = request.data.get('player_id')
        land = request.data.get('land_num')

        player = Player.objects.get(id=player_id)
        board = PlayerBoardStatus.objects.get(player_id=player)
        board_pos = self.queryset.filter(board_id=board)
        position = board_pos.get(board_id=board, position=land)

        # 처음 밭을 가는 경우
        if count_farmlands(board_pos) == 0:
            position.position_type = 2  # 밭
            position.save()
            serializer = self.serializer_class(position)
            return Response(serializer.data)
        # 인접한지 체크
        if not land in get_adjacent_farmlands(board_pos):
            return Response({'error': "That land is not adjacent with your farmland"}, status=403)
        position.position_type = 2  # 밭
        position.save()
        serializer = self.serializer_class(position)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='put',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'position': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=False, methods=['PUT'])
    def construct_room(self, request):
        player_id = request.data.get('player_id')
        position = request.data.get('position')

        player = Player.objects.get(id=player_id)
        board = PlayerBoardStatus.objects.get(player_id=player)
        board_pos = BoardPosition.objects.filter(board_id=board)
        slot = board_pos.get(position=position)

        resource = PlayerResource.objects.filter(player_id=player)

        tree = resource.get(resource_id=1)
        reed = resource.get(resource_id=3)
        soil = resource.get(resource_id=2)
        stone = resource.get(resource_id=4)

        if slot.position_type != 0:
            return Response({'error': 'That position is not an empty land'})

        reed.resource_num -= 2
        reed.save()

        if board.house_type == 0:
            tree.resource_num -= 5
            tree.save()
        elif board.house_type == 1:
            soil.resource_num -= 5
            soil.save()
        elif board.house_type == 2:
            stone.resource_num -= 5
            stone.save()

        slot.position_type = 1
        slot.save()
        board.house_num += 1
        board.save()
        serializer = self.serializer_class(slot)
        return Response({'message': 'contruct_room success', 'result': serializer.data})

    @swagger_auto_schema(
        method='put',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'position': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=False, methods=['PUT'])
    def construct_cowshed(self, request):
        player_id = request.data.get('player_id')
        position = request.data.get('position')

        player = Player.objects.get(id=player_id)
        board = PlayerBoardStatus.objects.get(player_id=player)
        board_pos = BoardPosition.objects.filter(board_id=board)
        slot = board_pos.get(position=position)

        resource = PlayerResource.objects.filter(player_id=player)

        tree = resource.get(resource_id=1)

        if slot.position_type == 1:
            return Response({'error': 'That position is a room'}, status=403)
        if slot.position_type in [4, 5]:
            return Response({'error': 'Thatt position already has a cowshed'}, status=403)

        # 충분한 자원이 있는지
        if tree.resource_num < 2:
            return Response({'error': 'That player seems not to have enough trees'})

        tree.resource_num -= 2
        tree.save()

        if slot.position_type == 0:
            slot.position_type = 4
        elif slot.position_type == 3:
            slot.position_type = 5
        slot.save()
        board.cowshed_num += 1
        board.save()
        serializer = self.serializer_class(slot)
        return Response({'message': 'contruct_cowshed success', 'result': serializer.data})

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=False, methods=['POST'])
    def get_all_position(self, request):  # { "player_id" : 1 }
        player_id = int(request.data.get('player_id'))
        board_status = PlayerBoardStatus.objects.get(player_id=player_id)
        board_status_id = board_status.id
        board_position = BoardPosition.objects.filter(board_id=board_status_id)
        board_position_arr = list(board_position)
        animal_type = []
        house_type = board_status.house_type
        for i in range(15):
            animal_type.append(0)
        pen_positions = PenPosition.objects.filter(board_id=board_status_id)
        if pen_positions.exists():
            for pen_position in pen_positions:
                position_list = eval(pen_position.position_list)
                for position in position_list:
                    animal_type[position - 1] = pen_position.animal_type
        serializer = self.serializer_class(board_position_arr, many=True)
        return Response({"house_type": house_type, "animal_type": animal_type, "position_arr": serializer.data})

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('type', openapi.IN_QUERY, description='room or cowshed', type=openapi.TYPE_STRING),
        ]
    )
    @action(detail=False, methods=['GET'])
    def get_available_slots(self, request):
        player_id = request.query_params.get('player_id')
        slot_type = request.query_params.get('slot_type')

        player = Player.objects.get(id=player_id)
        board = PlayerBoardStatus.objects.get(player_id=player)
        board_pos = BoardPosition.objects.filter(board_id=board)

        if slot_type == 'room':
            available_rooms = get_adjacent_rooms(board_pos)
            return Response({'available': available_rooms})
        if slot_type == 'cowshed':
            available_cowshed = get_available_cowshed(board_pos)
            return Response({'available': available_cowshed})

class FencePositionViewSet(ModelViewSet):
    queryset = FencePosition.objects.all()
    serializer_class = FencePositionSerializer

    def get_positionid(self, board_id, position):
        position_queryset = BoardPosition.objects.get(board_id=board_id, position=position)
        position_id = position_queryset.id
        return position_id

    def get_board_with_playerid(self, player_id):
        player = Player.objects.get(id=player_id)
        board_queryset = PlayerBoardStatus.objects.get(player_id=player)
        return board_queryset

    def get_fencepositions_with_boardid(self, board_id):
        positions = BoardPosition.objects.filter(board_id=board_id, position_type=3).values_list('position', flat=True)
        positions = list(positions)
        return positions  # int 배열

    def get_invalid_position(self, board_id):  # 집, 밭 포지션 가져오기
        position_query = BoardPosition.objects.filter(board_id=board_id, position_type=2).values_list('position', flat=True)
        positions = list(position_query)
        position_query = BoardPosition.objects.filter(board_id=board_id, position_type=1).values_list('position', flat=True)
        positions.extend(position_query)
        return positions

    def get_valid_position(self, ex_fence_list, invalid_position):  # fence_list에 있는 포지션들의 주변 포지션을 리턴
        if not ex_fence_list:  # 기존에 설치한 울타리가 없다면
            ls = list(range(3, 16))
            return list(set(ls) - set(invalid_position))
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

    def is_in_valid(self, fence_array, valid_position):  # 울타리를 치고 싶은 포지션이 valid한지 검증
        for positions in fence_array:  # [8] /  [[8], [5, 6, 9]]
            for position in positions:  # 8  /  5 6 9
                if position in valid_position:  # [9, 11, 15]
                    return positions
        return False

    @action(detail=False, methods=['POST'])
    def build_fence(self, request):  # { "player_id": 12, "fence_array": [[1, 2, 7], [6]] }
        player_id = request.data.get('player_id')
        board = self.get_board_with_playerid(player_id)
        board_id = board.id
        fst_fence_array = request.data.get('fence_array')  # 추가하고 싶은 울타리들의 포지션 배열
        fence_array = fst_fence_array
        ex_fence_array = self.get_fencepositions_with_boardid(board_id)  # 기존에 가지고 있던 울타리들의 포지션 배열
        invalid_position = self.get_invalid_position(board_id)  # 집, 밭 포지션
        valid_position = self.get_valid_position(ex_fence_array, invalid_position)  # fence_array에 포함되어야 하는 포지션
        print(f'player_id: {player_id}\nfence_array: {fence_array}\nex_fence_array: {ex_fence_array}\ninvalid_positioin: {invalid_position}\nvalid_position: {valid_position}')
        pen_num = len(fence_array)

        while (len(fence_array) > 0):  # 유효한 울타리인지 검사
            new_position = self.is_in_valid(fence_array, valid_position)
            print(f'new_position: {new_position}')
            if new_position == False:
                return Response({'error': 'wrong position.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                ex_fence_array.extend(new_position)
                valid_position = self.get_valid_position(ex_fence_array, invalid_position)
                fence_array = [sublist for sublist in fence_array if sublist != new_position]

        fence_array = fst_fence_array
        print('울타리치기 시작')

        # db에 추가
        fence_position_arr = []
        for fences in fence_array:
            for i in range(len(fences)):
                left, right, top, bottom = [True, True, True, True]
                if (int(fences[i]) % 3 != 0) & ((int(fences[i]) + 1) in fences):  # 오른쪽 끝 제외
                    right = False
                if (int(fences[i]) % 3 != 1) & ((int(fences[i]) - 1) in fences):  # 왼쪽 끝 제외
                    left = False
                if (int(fences[i]) + 3 < 16) & ((int(fences[i]) + 3) in fences):  # 맨 밑 제외
                    bottom = False
                if (int(fences[i]) - 3 > 0) & ((int(fences[i]) - 3) in fences):  # 맨 위 제외
                    top = False

                # 해당 포지션의 type을 3으로 바꿈
                position_id = self.get_positionid(board_id,
                                                  fences[i])  # board_id가 board_id인 객체 중 position이 fences[i]인 객체의 id
                board_position = BoardPosition.objects.get(id=position_id)
                board_position.position_type = 3
                board_position.save()

                # FencePosition 개체 생성 및 속성 설정
                fence_position = FencePosition()
                fence_position.position_id = board_position
                fence_position.player_id = player_id
                fence_position.left = left
                fence_position.right = right
                fence_position.top = top
                fence_position.bottom = bottom
                fence_position.save()

                fence_position_arr.append(fence_position)

                # player_board_status의 우리 개수 update
                player_board_status = PlayerBoardStatus.objects.get(id=board_id)
                pen = player_board_status.pen_num
                pen = pen + pen_num
                player_board_status.pen_num = pen
                player_board_status.save()

            # pen_position에 인스턴스 추가
            pen_position = PenPosition()
            pen_position.board_id = board
            pen_position.position_list = f"{fences}"
            pen_position.max_num = len(fences) * 2
            pen_position.save()

        serializer = self.serializer_class(fence_position_arr, many=True)

        return Response({"message": "fence update complete.", "position_arr": serializer.data},
                        status=status.HTTP_201_CREATED)


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

        chunked_subcards = [subfacilitycards[i:i + 7] for i in range(0, 14, 7)]  # 7개씩 두 묶음으로 나눕니다.
        serialized_data = []

        player1 = Player.objects.get(id=1)
        player2 = Player.objects.get(id=2)

        chunk1 = chunked_subcards[0]
        chunk2 = chunked_subcards[1]

        for sub_card in chunk1:
            PlayerCard.objects.create(player_id=player1, card_id=sub_card.card_id)

        for sub_card in chunk2:
            PlayerCard.objects.create(player_id=player2, card_id=sub_card.card_id)

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

        player1 = Player.objects.get(id=1)
        player2 = Player.objects.get(id=2)

        chunk1 = chunked_subcards[0]
        chunk2 = chunked_subcards[1]

        for job_card in chunk1:
            PlayerCard.objects.create(player_id=player1, card_id=job_card.card_id)

        for job_card in chunk2:
            PlayerCard.objects.create(player_id=player2, card_id=job_card.card_id)

        for chunk in chunked_subcards:
            serializer = JobCardSerializer(chunk, many=True)
            serialized_data.append(serializer.data)

        return Response(serialized_data)


class MainFacilityCardViewSet(ModelViewSet):
    queryset = MainFacilityCard.objects.all()
    serializer_class = MainFacilityCardSerializer

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'player_id': openapi.TYPE_INTEGER,
                'facility_id': openapi.TYPE_INTEGER,
                'animal_type': openapi.TYPE_INTEGER,
                'position': openapi.TYPE_INTEGER
            }
        )
    )
    @action(detail=False, methods=['post'])
    def cook_animal(self, request):
        player_id = request.data.get('player_id')
        fac_id = request.data.get('facility_id')
        animal_type = request.data.get('animal_type')
        position = request.data.get('position')

        player_obj = Player.objects.get(id=player_id)

        if not does_have_cooking_facility(player_obj):
            return Response({'error': 'That player has no facilites to cook'}, status=403)

        cards = PlayerCard.objects.filter(player_id=player_obj)
        found = False
        for card in cards:
            if card.card_id.id == fac_id:
                found = True
                break

        if not found:
            return Response({'error': 'That player doesn\'t have that facility'}, status=403)

        food = PlayerResource.objects.get(player_id=player_obj, resource_id=10)
        animal = PlayerResource.objects.get(player_id=player_obj, resource_id=animal_type + 6)
        if position == 0 and animal.resource_num > 0:
            animal.resource_num -= 1
            animal.save()
            # 화로
            if fac_id in [29, 30]:
                if animal_type in [1, 2]:  # 양, 돼지
                    food.resource_num += 2
                elif animal_type == 3:  # 소
                    food.resource_num += 2
                food.save()
            # 화덕
            elif fac_id in [31, 32]:
                if animal_type == 1:  # 양
                    food.resource_num += 2
                elif animal_type == 2:
                    food.resource_num += 3
                elif animal_type == 3:  # 소
                    food.resource_num += 4
                food.save()
            return Response({'message': 'Cooking Success'})
        elif position == 0:
            return Response({'error': 'That player seems to have no that type of animal'}, status=403)

        if not does_have_animal(player_obj, animal_type):
            return Response({'error': 'That player seems to have no that type of animal'}, status=403)

        board = PlayerBoardStatus.objects.get(player_id=player_obj)
        slot = BoardPosition.objects.filter(board_id=board).get(position=position)

        # 해당 칸에 동물이 없거나 가축 종류가 다른 경우
        if slot.animal_num == 0 or get_animal_type(board, position) != animal_type:
            return Response({'error': 'That position seems not to have that type of animal'}, status=403)

        # 화로
        if fac_id in [29, 30]:
            if animal_type in [1, 2]:  # 양, 돼지
                food.resource_num += 2
            elif animal_type == 3:  # 소
                food.resource_num += 2
            food.save()
        # 화덕
        elif fac_id in [31, 32]:
            if animal_type == 1:  # 양
                food.resource_num += 2
            elif animal_type == 2:
                food.resource_num += 3
            elif animal_type == 3:  # 소
                food.resource_num += 4
            food.save()
        # 칸에서 동물수 줄임
        slot.animal_num -= 1
        slot.save()
        # 우리에도 반영
        pen = get_pen_by_postiion(board, position)
        pen.current_num -= 1
        pen.save()
        if pen.current_num == 0:
            pen.animal_type = 0
            pen.save()
        return Response({'message': 'Cooking Success'})


class ActionBoxViewSet(ModelViewSet):
    queryset = ActionBox.objects.all()
    serializer_class = ActionBoxSerializer

    @action(detail=False, methods=['get'])
    def get_actions_with_pid(self, request):
        familyposition = FamilyPosition.objects.all()
        response_list = []
        for action in self.queryset:
            action.refresh_from_db()
            if action.is_occupied:
                act = familyposition.get(action_id=action)
                pid = act.player_id.id
                try:
                    obj = {
                        "player_id":pid,
                        "action_id":act.action_id.id,
                        "action_name":act.action_id.name,
                        "acc_resource":act.action_id.acc_resource,
                        "add_resource":act.action_id.add_resource,
                        "round":act.action_id.round,
                        "is_res":act.action_id.is_res,
                        "is_occupied": act.action_id.is_occupied,
                        "card_id":act.action_id.card_id.id
                    }
                except AttributeError:
                    obj = {
                        "player_id":pid,
                        "action_id":act.action_id.id,
                        "action_name":act.action_id.name,
                        "acc_resource":act.action_id.acc_resource,
                        "add_resource":act.action_id.add_resource,
                        "round":act.action_id.round,
                        "is_res":act.action_id.is_res,
                        "is_occupied": act.action_id.is_occupied,
                        "card_id":None
                    }
                response_list.append(obj)
            else:
                try:
                    obj = {
                        "player_id":-1,
                        "action_id":action.id,
                        "action_name":action.name,
                        "acc_resource":action.acc_resource,
                        "add_resource":action.add_resource,
                        "round":action.round,
                        "is_res":action.is_res,
                        "is_occupied": action.is_occupied,
                        "card_id":action.card_id.id
                    }
                except AttributeError:
                    obj = {
                        "player_id":-1,
                        "action_id":action.id,
                        "action_name":action.name,
                        "acc_resource":action.acc_resource,
                        "add_resource":action.add_resource,
                        "round":action.round,
                        "is_res":action.is_res,
                        "is_occupied": action.is_occupied,
                        "card_id":None
                    }
                response_list.append(obj)
        return Response(response_list)

class GameStatusViewSet(ModelViewSet):
    queryset = GameStatus.objects.all()
    serializer_class = GameStatusSerializer

    @action(detail=False, methods=['get'])
    def get_turn(self, request):
        game_status = self.get_queryset().first()  # Assuming there is only one GameStatus instance
        turn_counter = game_status.turn
        return Response({'turn': turn_counter})

    @swagger_auto_schema(
        method='get',
        request_body=None
    )
    @action(detail=False, methods=['get'])
    def round_end(self, request):
        players = Player.objects.all()
        fstplayer = FstPlayer.objects.first()
        for player in players:
            # 어른 말수 재할당
            player.adult_num += player.baby_num
            player.remain_num = player.adult_num
            player.baby_num = 0
            if player.fst_player:
                fstplayer.player_id = player.id
                fstplayer.save()
            player.save()
            #is_fam True
            board_positions = BoardPosition.objects.filter(position_type=1)
            adult_num = player.adult_num
            for board_position in board_positions:
                if adult_num == 0:
                    break
                if board_position.is_fam == False:
                    board_position.is_fam = True
                    adult_num -= 1
                    board_position.save()
        #action box is_occupied False
        actionboxes = ActionBox.objects.all()
        for actionbox in actionboxes:
            if actionbox.is_res:
                actionbox.acc_resource += actionbox.add_resource
            else:
                actionbox.acc_resource = actionbox.add_resource
            actionbox.is_occupied = False
            actionbox.save()
        #라운드 증가, turn = 1로 세팅
        game_status = GameStatus.objects.first()
        game_status.round += 1
        game_status.turn = 1
        game_status.save()
        #게임판에서 가족말 제거
        familyposition = FamilyPosition.objects.all()
        familyposition.delete()

        return Response({'next round': game_status.round, 'turn': game_status.turn})

    @action(detail=False, methods=['get'])
    def period_end1(self, request):
        players = Player.objects.all()
        for player in players:
            playerBoard = PlayerBoardStatus.objects.get(player_id = player.id)
            boardPositions = BoardPosition.objects.filter(board_id = playerBoard.id)
            # (수확1번) 1️⃣,2️⃣작물이 심어져 있는 밭에서 곡식/채소 1개씩 수확
            for boardPosition in boardPositions:
                if boardPosition.position_type == 2 and boardPosition.vege_num != 0:
                    boardPosition.vege_num -= 1
                    playerResource = PlayerResource.objects.get(player_id=player.id, resource_id=boardPosition.vege_id)
                    playerResource.resource_num += 1
                    playerResource.save()
            # (수확2번) 1️⃣,2️⃣가족 먹여살리기
            playerfood = PlayerResource.objects.get(player_id=player, resource_id=10)
            consume = player.adult_num*2 + player.baby_num*2
            playerfood.resource_num -= consume
            hungrytoken = PlayerResource.objects.get(player_id=player, resource_id=11)
            while playerfood.resource_num < 0 :
                hungrytoken.resource_num += 1
                playerfood.resource_num += 1
            playerfood.save()
            hungrytoken.save()
        return Response({'message':'next period'})
    
    @action(detail=False, methods=['get'])
    def period_end2(self, request):
        # (수확3번) 1️⃣,2️⃣동물 번식
        pos = request.data.get('pos_id')
        players = Player.objects.all()
        for player in players:
            playerBoard = PlayerBoardStatus.objects.get(player_id = player.id)
            boardPositions = BoardPosition.objects.filter(board_id = playerBoard)
            #양 : 1
            sheep = PlayerResource.objects.get(player_id=player.id, resource_id=7)
            if sheep.resource_num >= 2 and animal_check(player, 1) >= 1:
                animal_breed(player, 1, pos)
            #돼지 : 2
            pig = PlayerResource.objects.get(player_id=player.id, resource_id=8)
            if pig.resource_num >= 2 and animal_check(player, 2) >= 1:
                animal_breed(player, 2, pos)
            #소 : 3
            cow = PlayerResource.objects.get(player_id=player.id, resource_id=9)
            if cow.resource_num >= 2 and animal_check(player, 3) >= 1:
                animal_breed(player, 3, pos)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def my_turn(self, request):
        player_id = request.query_params.get('player_id')

        another_player = Player.objects.exclude(id=player_id).first()
        game_status = self.get_queryset().first()
        turn_counter = game_status.turn
        origin = FstPlayer.objects.first()

        is_first_player_turn = turn_counter % 2 == 1

        result = another_player.remain_num == 0 or (is_first_player_turn and int(player_id) == origin.player_id) or (not is_first_player_turn and int(player_id) != origin.player_id)

        return Response({'my_turn': result})


class FamilyPositionViewSet(ModelViewSet):
    queryset = FamilyPosition.objects.all()
    serializer_class = FamilyPositionSerializer

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'turn': openapi.Schema(type=openapi.TYPE_INTEGER),
                'player_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'action_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'card_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['turn', 'player_id', 'action_id']
        )
    )
    @action(detail=False, methods=['post'])
    def take_action(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Load the player ID and action ID from the request data
        player_id = int(request.data.get('player_id'))
        action_id = int(request.data.get('action_id'))
        card_id = int(request.data.get('card_id'))

        # Get the player and action objects
        player = Player.objects.get(id=player_id)
        card = None
        try:
            card = Card.objects.get(id=card_id)
        except Card.DoesNotExist:
            pass
        another_player = Player.objects.exclude(id=player_id).first()
        action = ActionBox.objects.get(id=action_id)

        # Get the current turn counter from the game_status table
        game_status = GameStatus.objects.first()
        turn_counter = game_status.turn
        origin = FstPlayer.objects.first()

        # Check whose turn it is based on the turn counter
        is_first_player_turn = turn_counter % 2 == 1

        response = None

        # Check if it's the player's turn
        # 상대방의 가족 구성원이 없거나, 자신의 차례일 경우
        if another_player.remain_num == 0 or (is_first_player_turn and player_id == origin.player_id) or (not is_first_player_turn and player_id != origin.player_id):
            # Action id 별로 메소드 호출

            # 덤불
            if action_id == 1:
                # perform_action_1()
                pass
            # 수풀
            elif action_id == 2:
                # perform_action_2()
                pass
            #교습
            elif action_id == 5:
                response = lesson(player, card)

            # 농장 확장
            elif action_id == 8:
                response = farm_extension(player)
                if response.status_code != 404:
                    act = ActionBox.objects.get(id=8)
                    act.is_occupied = True
                    act.save()
            # 회합장소
            elif action_id == 9:
                response = meeting_place(player)
            # 곡식종자
            elif action_id == 10:
                response = grain_seed(player)
            # 숲
            elif action_id == 11:
                response = forest(player)
            # 농지
            elif action_id == 12:
                response = farmland(player)
            # 흙 채굴장
            elif action_id == 13:
                response = soil_mining(player)
            # 갈대밭
            elif action_id == 14:
                response = reed_field(player)
            #날품팔이
            elif action_id == 15:
                response = day_laborer(player)
            #낚시
            elif action_id == 16:
                response = fishing(player)
            # 양시장
            elif action_id == 18:
                response = sheep_market(player)
            # 곡식활용
            elif action_id == 19:
                response = baking(player, card_id)
            # 주요설비
            elif action_id == 20:
                response = facility(player, card)
            # 집개조
            elif action_id == 21:
                player_card = PlayerCardViewSet()
                result = player_card.activable_check(
                    request=type('DummyRequest', (object,), {'data': {'player_id': player_id}})())
                if result:
                    response = house_upgrade(player)
                    player_card.activate_card(request=type('DummyRequest', (object,),
                                                           {'data': {'player_id': player_id, 'card_id': card_id}})())
                else:
                    return Response({'error': 'You can\'t activate some card'}, status=status.HTTP_403_FORBIDDEN)
            #서부채석장
            elif action_id == 22:
                response = west_mine(player)
            # 기본 가족 늘리기
            elif action_id == 23:
                response = add_fam(player, card)
            # 돼지시장
            elif action_id == 24:
                #perfrom_action_24()
                pass
            #채소종자
            elif action_id == 25:
                response = vege_seed(player)
                pass
            #소시장
            elif action_id == 26:
                #perfrom_action_26()
                pass
            #동부채석장
            elif action_id == 27:
                response = east_mine(player)
            # 코드가 404면 -> 해당 행동이 거부됨 ->함수 종료
            if response.status_code == 404:
                return response

            # 턴 카운터 업데이트
            game_status.turn = turn_counter + 1
            game_status.save()

            # FamilyPosition에 데이터 추가
            new_instance = FamilyPosition.objects.create(player_id=player, action_id=action, turn=turn_counter)
            new_instance.save()

            # 가족 구성원 수 업데이트
            if player.remain_num != 0:
                player.remain_num -= 1
                player.save()
                board = PlayerBoardStatus.objects.get(player_id=player)
                pos = BoardPosition.objects.filter(board_id=board).get(position=1)
                if pos.is_fam:
                    pos.is_fam = False
                else:
                    pos = BoardPosition.objects.filter(board_id=board).get(position=2)
                    pos.is_fam = False
                pos.save()
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
            openapi.Parameter('resource_id', openapi.IN_QUERY, description='Resource ID', type=openapi.TYPE_INTEGER,
                              required=False),
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
            openapi.Parameter('type', openapi.IN_QUERY, description='adult or baby', type=openapi.TYPE_STRING,
                              required=False),
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
            return Response({'player_id': int(player_id), 'adult': adult, 'baby': baby})
        elif type == "adult":
            return Response({'player_id': int(player_id), 'adult': adult})
        elif type == 'baby':
            return Response({'player_id': int(player_id), 'baby': baby})
        else:
            return Response({'message': 'Invalid type'}, status=400)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
            openapi.Parameter('type', openapi.IN_QUERY, description='cowshed or fence', type=openapi.TYPE_STRING,
                              required=False),
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
            return Response({'player_id': int(player_id), 'cowshed': cowshed, 'fence': fence})
        elif type == "cowshed":
            return Response({'player_id': int(player_id), 'cowshed': cowshed})
        elif type == 'fence':
            return Response({'player_id': int(player_id), 'fence': fence})
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
        player_id = int(request.data.get('player_id'))
        resource_id = int(request.data.get('resource_id'))
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
                    return Response({'player_id': int(player_id), 'cowshed': board.cowshed_num})
                elif type == 'fence' and fence >= -num:
                    board.fence_num += num
                    board.save()
                    return Response({'player_id': int(player_id), 'fence': board.fence_num})
                else:
                    return Response({'message': 'resource cannot be negative'}, status=400)
            else:
                if type == 'cowshed':
                    board.cowshed_num += num
                    board.save()
                    return Response({'player_id': int(player_id), 'cowshed': board.cowshed_num})
                elif type == 'fence':
                    board.fence_num += num
                    board.save()
                    return Response({'player_id': int(player_id), 'fence': board.fence_num})
        except PlayerBoardStatus.DoesNotExist:
            return Response({'message': 'PlayerBoardStatus not found.'}, status=404)


class PlayerCardViewSet(ModelViewSet):
    queryset = PlayerCard.objects.all()
    serializer_class = PlayerCardSerializer

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('player_id', openapi.IN_QUERY, description='Player ID', type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_activate_card(self, request):
        my_id = request.query_params.get('player_id')
        activate_cards = PlayerCard.objects.filter(player_id=my_id, activate=1)
        serialized_data = []
        for activate_card in activate_cards:
            serializer = PlayerCardSerializer(activate_card)
            serialized_data.append(serializer.data)

        return Response(serialized_data)

    @action(detail=False, methods=['get'])
    def activable_check(self, request):
        my_id = request.data.get('player_id')
        my_cardlist = PlayerCard.objects.filter(player_id=my_id, activate=0)
        serialized_data = []
        for my_card in my_cardlist:
            flag = 1
            card_costs = ActivationCost.objects.filter(card_id=my_card.card_id)
            for card_cost in card_costs:
                my_resource = PlayerResource.objects.get(player_id=my_id, resource_id=card_cost.resource_id)
                if my_resource.resource_num < card_cost.resource_num:
                    flag = 0
                    break
            if flag == 1:
                serializer = PlayerCardSerializer(my_card)
                serialized_data.append(serializer.data)
        main_cardlist = MainFacilityCard.objects.filter(player_id=0)
        for main_card in main_cardlist:
            flag = 1
            card_costs = ActivationCost.objects.filter(card_id=main_card.card_id)
            for card_cost in card_costs:
                my_resource = PlayerResource.objects.get(player_id=my_id, resource_id=card_cost.resource_id)
                if my_resource.resource_num < card_cost.resource_num:
                    flag = 0
                    break
            if flag == 1:
                serializer = MainFacilityCardSerializer(main_card)
                serialized_data.append(serializer.data)

        return Response(serialized_data)

    @action(detail=False, methods=['put'])
    def activate_card(self, request):
        # 어떤플레이어가 어떤카드를 활성화시킬건지
        my_id = int(request.data.get('player_id'))
        player = Player.objects.get(id=my_id)
        choice_card = int(request.data.get('card_id'))

        # 활성화 가능 여부 check
        active_costs = ActivationCost.objects.filter(card_id=choice_card)
        for active_cost in active_costs:
            my_resource = PlayerResource.objects.get(player_id=my_id, resource_id=active_cost.resource_id)
            if my_resource.resource_num < active_cost.resource_num:
                return Response({'detail': 'Not enough resources'}, status=404)
        # 주요설비일때
        if 29 <= choice_card <= 38:
            active_card = MainFacilityCard.objects.get(card_id=choice_card)
            active_costs = ActivationCost.objects.filter(card_id=choice_card)
            for active_cost in active_costs:
                my_resource = PlayerResource.objects.get(player_id=my_id, resource_id=active_cost.resource_id)
                my_resource.resource_num -= active_cost.resource_num
                my_resource.save()
            active_card.player_id = my_id
            active_card.save()
            PlayerCard.objects.create(activate=1, player_id=player, card_id=active_card.card_id)
            return Response({'message': 'Activate Success'})
        # 보조설비, 직업카드일때
        else:
            active_card = PlayerCard.objects.get(card_id=choice_card)
            if active_card.player_id != player:
                return Response({'detail': 'This is not your card'}, status=404)
            active_costs = ActivationCost.objects.filter(card_id=choice_card)
            for active_cost in active_costs:
                my_resource = PlayerResource.objects.get(player_id=my_id, resource_id=active_cost.resource_id)
                my_resource.resource_num -= active_cost.resource_num
                my_resource.save()
            active_card.activate = 1
            active_card.save()
            return Response({'message': 'Activate Success'})


class PenPositionViewSet(ModelViewSet):
    queryset = PenPosition.objects.all()
    serializer_class = PenPositionSerializer

class FstPlayerViewSet(ModelViewSet):
    queryset = FstPlayer.objects.all()
    serializer_class = FstPlayerSerializer