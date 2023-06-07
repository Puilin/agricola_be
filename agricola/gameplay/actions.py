from .models import *
from .serializer import *
from rest_framework.response import Response
from .utils import count_farmlands, get_adjacent_farmlands

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

    #곡식용 삽이 있을 때
    try:
        shovel = PlayerCard.objects.get(player_id = player.id, card_id = 22)
        if shovel.activate == 1:
            my_resource.resource_num += 1
    except PlayerCard.DoesNotExist:
        pass

    my_resource.save()

    serializer = PlayerResourceSerializer(my_resource)
    return Response(serializer.data)

def house_upgrade(player):
    house_action = ActionBox.objects.get(id=21)
    #집개조 칸에 누군가 있으면
    if house_action.is_occupied:
        return Response({'detail': 'There\'s someone else in house upgrade'}, status=404)
    #집개조 칸에 이제 사람이 있음
    house_action.is_occupied = True
    house_action.save()

    my_board = PlayerBoardStatus.objects.get(player_id=player.id)
    reed = PlayerResource.objects.get(player_id=player.id, resource_id=3)
    #나무집 -> 흙집
    if my_board.house_type == 1:
        soil = PlayerResource.objects.get(player_id=player.id, resource_id=2)
        if reed.resource_num >= my_board.house_num and soil.resource_num >= my_board.house_num:
            reed.resource_num -= my_board.house_num
            soil.resource_num -= my_board.house_num
            my_board.house_type = 2
            soil.save()
        else:
            return Response({'detail': 'Not enough resources'}, status=404)
    #흑집 -> 돌집    
    elif my_board.house_type == 2:
        stone = PlayerResource.objects.get(player_id=player.id, resource_id=4)
        if reed.resource_num >= my_board.house_num and stone.resource_num >= my_board.house_num:
            reed.resource_num -= my_board.house_num
            stone.resource_num -= my_board.house_num
            my_board.house_type = 3
            stone.save()
        else:
            return Response({'detail': 'Not enough resources'}, status=404)
    else:
        return Response({'detail': 'You can no longer upgrade'}, status=404)
    reed.save()
    my_board.save()

    serializer = PlayerBoardStatusSerializer(my_board)
    return Response(serializer.data)

def farmland(player):
    farmland_action = ActionBox.objects.get(id=12)
    #농지 칸에 누군가 있으면
    if farmland_action.is_occupied:
        return Response({'detail': 'There\'s someone else in farmland'}, status=404)
    #농지 칸에 이제 사람이 있음
    farmland_action.is_occupied = True
    farmland_action.save()

    board = PlayerBoardStatus.objects.get(player_id=player)
    board_pos = BoardPosition.objects.filter(board_id=board) # queryset
    
    if count_farmlands(board_pos) == 0: # 처음 밭을 가는 경우
        empty_lands = board_pos.filter(position_type=0) # 빈땅 리스트
        board_pos_list = empty_lands.values_list('position', flat=True) # 포지션 번호만 추출
        return Response({'lands':board_pos_list})
    else: # 밭이 하나 이상일 경우
        possible_positions = get_adjacent_farmlands(board_pos)
        return Response({'lands':possible_positions})