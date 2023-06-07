from .models import *
from .serializer import *
from rest_framework.response import Response

# 밭 개수 받아오는 함수
# board_pos := queryset(Boardposition)
def count_farmlands(board_pos):
    count = 0
    for slot in board_pos:
        if slot.position_type == 2:
            count += 1
    return count

# 밭 건설 유효성 체크
def is_invalid_farmlands(farmlands, index, dir):
    if index in [1,2]:
        return False
    elif index % 3 == 0 and dir == -1:
        return False
    elif index % 3 == 1 and dir == 1:
        return False
    elif index >= 16:
        return False
    elif index in farmlands:
        return False
    else:
        return True

# 상 좌 우 하 순서로 유효한지 검사후 유효한 밭번호 반환
def get_adjacent_slots(farmlands, index):
    dircetions = [-3, -1, 1, 3]
    result = []
    for dir in dircetions:
        if not is_invalid_farmlands(farmlands, index + dir, dir):
            continue
        result.append(index+dir)
    return result


# 밭이 하나 이상일 경우 설치가능한 (인접한) 밭의 번호 받아오는 함수
def get_adjacent_farmlands(board_pos):
    farmlands = board_pos.filter(position_type=2).values_list('position', flat=True) # 밭 번호 리스트
    lists = []
    for index in farmlands:
        lists += get_adjacent_slots(farmlands, index)
    return list(set(lists))

# 가축을 키울수 있는 칸의 수를 받아오는 함수
def count_pens(board_pos):
    fence_only = board_pos.filter(position_type=3).count()
    cowshed_only = board_pos.filter(position_type=4).count()
    fence_and_cowshed = board_pos.filter(position_type=5).count()

    return fence_only + cowshed_only + fence_and_cowshed

def does_have_cooking_facility(player):
    deck = PlayerCard.objects.filter(player_id=player)
    activated_card_ids = deck.filter(activate=1).values_list('card_id', flat=True)
    for id in activated_card_ids:
        #화로1, 화로2, 화덕1, 화덕2
        if id in [29, 30, 31, 32]:
            return True
    return False

# 칸 번호로 가축 종류 받아오는 함수
def get_animal_type(board, position):
    pens_array = PenPosition.objects.filter(board_id=board).values_list('position_list') # 요청받은 번호에 해당하는 우리
    for list_str in pens_array:
        if position in eval(list_str):
            return PenPosition.objects.filter(board_id=board).get(position_list=list_str).animal_type
    return 0

def update_animal_type(board, position, animal_type):
    pens_array = PenPosition.objects.filter(board_id=board).values_list('position_list') # 요청받은 번호에 해당하는 우리
    for list_str in pens_array:
        if position in eval(list_str):
            penpos = PenPosition.objects.filter(board_id=board)
            pen = penpos.get(position_list=list_str)
            pen.animal_type = animal_type
            pen.save()
            return True
    return False