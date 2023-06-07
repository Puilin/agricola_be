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
    pens = board_pos.filter(position_type=2)