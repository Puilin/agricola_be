from .models import *
from .serializer import *
from rest_framework.response import Response
from .utils import *
from django.db.models import Q


def forest(player):
    forest_action = ActionBox.objects.get(id=11)
    my_resource = PlayerResource.objects.get(player_id=player.id, resource_id=1)
    # 숲에 누군가 있으면
    if forest_action.is_occupied:
        return Response({'detail': 'There\'s someone else in forest.'}, status=404)
    if forest_action.acc_resource > 0:
        # 숲에 이제 사람이 있음
        forest_action.is_occupied = True
        # 숲에서 나무를 몽땅 없앰
        forest_action.acc_resource -= forest_action.acc_resource
        # 플레이어의 자원에 추가
        my_resource.resource_num += forest_action.acc_resource

        # db에 저장
        forest_action.save()
        my_resource.save()

        serializer = PlayerResourceSerializer(my_resource)
        return Response(serializer.data)
    else:
        return Response({'detail': 'There\'s no exisiting resources.'}, status=404)


def grain_seed(player):
    grain_action = ActionBox.objects.get(id=10)
    my_resource = PlayerResource.objects.get(player_id=player.id, resource_id=5)
    # 곡식 종자 칸에 누군가 있으면
    if grain_action.is_occupied:
        return Response({'detail': 'There\'s someone else in grain seed'}, status=404)
    # 곡식종자 칸에 이제 사람이 있음
    grain_action.is_occupied = True
    grain_action.save()

    # 곡식을 하나 받음
    my_resource.resource_num += 1

    # 곡식용 삽이 있을 때
    try:
        shovel = PlayerCard.objects.get(player_id=player.id, card_id=22)
        if shovel.activate == 1:
            my_resource.resource_num += 1
    except PlayerCard.DoesNotExist:
        pass

    my_resource.save()

    serializer = PlayerResourceSerializer(my_resource)
    return Response(serializer.data)


def house_upgrade(player):
    house_action = ActionBox.objects.get(id=21)
    # 집개조 칸에 누군가 있으면
    if house_action.is_occupied:
        return Response({'detail': 'There\'s someone else in house upgrade'}, status=404)
    # 집개조 칸에 이제 사람이 있음
    house_action.is_occupied = True
    
    my_board = PlayerBoardStatus.objects.get(player_id=player.id)
    reed = PlayerResource.objects.get(player_id=player.id, resource_id=3)
    # 나무집 -> 흙집
    if my_board.house_type == 0:
        soil = PlayerResource.objects.get(player_id=player.id, resource_id=2)
        if reed.resource_num >= my_board.house_num and soil.resource_num >= my_board.house_num:
            reed.resource_num -= my_board.house_num
            soil.resource_num -= my_board.house_num
            my_board.house_type = 1
            soil.save()
        else:
            return Response({'detail': 'Not enough resources'}, status=404)
    # 흙집 -> 돌집
    elif my_board.house_type == 1:
        stone = PlayerResource.objects.get(player_id=player.id, resource_id=4)
        if reed.resource_num >= my_board.house_num and stone.resource_num >= my_board.house_num:
            reed.resource_num -= my_board.house_num
            stone.resource_num -= my_board.house_num
            my_board.house_type = 2
            stone.save()
        else:
            return Response({'detail': 'Not enough resources'}, status=404)
    else:
        return Response({'detail': 'You can no longer upgrade'}, status=404)
    house_action.save()
    reed.save()
    my_board.save()

    serializer = PlayerBoardStatusSerializer(my_board)
    return Response(serializer.data)


def farmland(player):
    farmland_action = ActionBox.objects.get(id=12)
    # 농지 칸에 누군가 있으면
    if farmland_action.is_occupied:
        return Response({'detail': 'There\'s someone else in farmland'}, status=404)
    # 농지 칸에 이제 사람이 있음
    farmland_action.is_occupied = True
    farmland_action.save()

    board = PlayerBoardStatus.objects.get(player_id=player)
    board_pos = BoardPosition.objects.filter(board_id=board)  # queryset
    
    if count_farmlands(board_pos) == 0:  # 처음 밭을 가는 경우
        empty_lands = board_pos.filter(position_type=0)  # 빈땅 리스트
        board_pos_list = empty_lands.values_list('position', flat=True)  # 포지션 번호만 추출
        return Response({'lands': board_pos_list})
    else:  # 밭이 하나 이상일 경우
        possible_positions = get_adjacent_farmlands(board_pos)
        return Response({'lands': possible_positions})


def sheep_market(player):
    sheep_market_action = ActionBox.objects.get(id=18)
    if sheep_market_action.is_occupied:
        return Response({'detail': 'There\'s someone else in sheepmarket'}, status=404)
    
    sheep_market_action.is_occupied = True
    sheep_market_action.save()

    board = PlayerBoardStatus.objects.get(player_id=player)
    board_pos = BoardPosition.objects.filter(board_id=board)  # queryset

    # 양시장 이용 조건 체크
    cond1, cond2 = True, True
    # 양을 키울수 있는 공간이 있는지 체크
    if count_pens(board_pos) == 0:
        cond1 = False
    
    # 양을 식량으로 바꿀 수 있는 설비가 있는지 체크
    if not does_have_cooking_facility(player):
        cond2 = False

    if cond1 and cond2:
        return Response({"case": 1, "massege": "You can raise them(it) or cook them (it)"}, status=200)
    elif cond1:
        return Response({"case": 2, "massege": "You can raise them(it)"}, status=200)
    elif cond2:
        return Response({"case": 3, "massege": "You can cook them(it)"}, status=200)
    else:
        sheep_market_action.is_occupied = False
        sheep_market_action.save()
        return Response({"case": 0, "error": "You don't have neither pens nor main facilities for cooking"}, status=404)


# 23번 행동칸: 기본 가족 늘리기
def add_fam(player):
    add_fam_action = ActionBox.objects.get(id=23)
    my_board = PlayerBoardStatus.objects.get(player_id=player.id)
    player = Player.objects.get(id=player.id)
    my_subfac_card = PlayerCard.objects.filter(
        Q(player_id=player.id) &
        Q(activate=1) &
        Q(card_id__in=range(15, 29)))  # 29는 포함X

    # 1. '기본가족늘리기' 칸에 다른 말이 있는지 확인
    # 다른 말이 이미 있는 경우 404
    if add_fam_action.is_occupied:
        return Response({'detail': 'There\'s someone else in the action box.'}, status=404)
    # 아무도 없다면 내 말 놓기
    else:
        add_fam_action.is_occupied = True
        add_fam_action.save()

    # 2. player에게 빈 방이 있어야만 가족 늘리기
    # 빈 방이 있는 경우: 신생아 1명 태어나고, 이 신생아는 23번 행동칸에 올라감
    if my_board.house_num > (player.adult_num + player.baby_num):
        player.baby_num += 1
        player.remain_num -= 1
    # 빈 방이 없는 경우 404
    else:
        return Response({'detail': 'There are no empty rooms.'}, status=404)

    # 3. 한 후에 보조설비 하나 내기(활성화하기)
    # player가 가진 보조설비 카드 보여주기 (대신 활성화되지 않은 카드만)
    serializer = PlayerCardSerializer(my_subfac_card, many=True)
    return Response(serializer.data)
    # player가 그 중 하나를 고른다
    # 고른 카드의 활성화 비용만큼 개인자원판에 있는지 확인
        # 개인 자원판에서 activation cost만큼 차감한다
        # “이 카드를 활성화하기 위한 자원이 부족합니다” 하고 다시 보조설비 카드를 보여준다
    # 구입한 보조설비 카드기 활성화 된다
