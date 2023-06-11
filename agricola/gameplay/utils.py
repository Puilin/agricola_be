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

# 건설 유효성 체크
def is_valid_slot(lands, index, dir):
    if index in [1,2]:
        return False
    elif index % 3 == 0 and dir == -1:
        return False
    elif index % 3 == 1 and dir == 1:
        return False
    elif index >= 16:
        return False
    elif index <= 0:
        return False
    elif index in lands:
        return False
    else:
        return True

# 상 좌 우 하 순서로 유효한지 검사후 유효한 칸 번호 반환
def get_adjacent_slots(lands, index):
    dircetions = [-3, -1, 1, 3]
    result = []
    for dir in dircetions:
        if not is_valid_slot(lands, index + dir, dir):
            continue
        result.append(index+dir)
    return result

# get_adjacent_slots 상위 호환. 인접하면서 빈땅이어야 함 (방을 늘리기 위해)
def check_adjacent_rooms(board_pos, lands, index):
    dircetions = [-3, -1, 1, 3]
    result = []
    for dir in dircetions:
        try:
            pos_type = board_pos.get(position=index+dir).position_type
            if pos_type != 0:
                continue
        except:
            pass
        if not is_valid_slot(lands, index + dir, dir):
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

# 설치가능한 (인접한) 방의 번호 받아오는 함수
def get_adjacent_rooms(board_pos):
    rooms = board_pos.filter(position_type=1).values_list('position', flat=True) # 방 번호 리스트
    lists = []
    for index in rooms:
        lists += check_adjacent_rooms(board_pos, rooms, index)
    return list(set(lists))

# 가축을 키울수 있는 칸의 수를 받아오는 함수
def count_pens(board_pos):
    fence_only = board_pos.filter(position_type=3).count()
    cowshed_only = board_pos.filter(position_type=4).count()
    fence_and_cowshed = board_pos.filter(position_type=5).count()

    return fence_only + cowshed_only + fence_and_cowshed

def does_have_cooking_facility(player):
    deck = PlayerCard.objects.filter(player_id=player)
    card_ids = deck.values_list('card_id', flat=True)
    for id in card_ids:
        #화로1, 화로2, 화덕1, 화덕2
        if id in [29, 30, 31, 32]:
            return True
    return False

def does_have_baking_facility(player):
    deck = PlayerCard.objects.filter(player_id=player)
    card_ids = deck.values_list('card_id', flat=True)
    for id in card_ids:
        #화로1, 화로2, 화덕1, 화덕2
        if id in [29, 30, 31, 32, 33, 34]:
            return True
    return False

# 칸 번호로 가축 종류 받아오는 함수
def get_animal_type(board, position):
    pens_array = PenPosition.objects.filter(board_id=board).values_list('position_list') # 요청받은 번호에 해당하는 우리
    for list_str in pens_array:
        if position in eval(list_str[0]):
            return PenPosition.objects.filter(board_id=board).get(position_list=list_str[0]).animal_type
    return -1

def update_animal_type(board, position, animal_type):
    pens_array = PenPosition.objects.filter(board_id=board).values_list('position_list') # 요청받은 번호에 해당하는 우리
    for list_str in pens_array:
        if position in eval(list_str[0]):
            penpos = PenPosition.objects.filter(board_id=board)
            pen = penpos.get(position_list=list_str[0])
            pen.animal_type = animal_type
            pen.save()
            return True
    return False

# 가축 종류로 우리(pen) queryset을 받아오는 함수
def get_pens(board, animal_type):
    pens = PenPosition.objects.filter(board_id=board)
    animal_pens = pens.filter(animal_type=animal_type)
    return animal_pens

# 칸 번호로 그 칸이 속한 우리 객체를 받아오는 함수
def get_pen_by_postiion(board, position):
    pens = PenPosition.objects.filter(board_id=board)
    pens_array = pens.values_list('position_list') # 요청받은 번호에 해당하는 우리
    for list_str in pens_array:
        if position in eval(list_str[0]):
            return pens.get(position_list=list_str[0])
    return None

# 플레이어가 특정 가축을 소유하고 있는지 체크하는 함수
def does_have_animal(player, animal_type):
    board = PlayerBoardStatus.objects.get(player_id=player)
    pens = PenPosition.objects.filter(board_id=board)
    animal_pens = pens.filter(animal_type=animal_type)
    if not animal_pens:
        return False
    return True

# 외양간을 지을 수 있는 칸 번호를 받아오는 함수
def get_available_cowshed(board_pos):
    empty_lands = board_pos.filter(position_type=0).values_list('position', flat=True)
    pens = board_pos.filter(position_type=3).values_list('position', flat=True)
    return list(empty_lands) + list(pens)

# 동물 추가 가능확인 함수 (animal = 양:1, 돼지:2, 소:3)
def animal_check(player, animal):
    p_board = PlayerBoardStatus.objects.get(player_id = player.id)
    able_num = 0
    #우리에 빈자리가 있음
    pens = PenPosition.objects.filter(board_id = p_board, animal_type = animal)
    for pen in pens:
        if pen.max_num > pen.current_num:
            able_num += (pen.max_num - pen.current_num)
    #빈 외양간이 있음
    board_poses = BoardPosition.objects.filter(board_id = p_board, position_type = 4)
    for board_pos in board_poses:
        if board_pos.animal_num == 0:
            able_num += 1

    return able_num

# 동물 번식
def animal_breed(player, animal, pos):
    p_board = PlayerBoardStatus.objects.get(player_id = player.id)
    board_pos = BoardPosition.objects.get(board_id = p_board.id, position = pos)
    p_resource = PlayerResource.objects.get(player_id = player.id, resource_id = animal+6)
    if board_pos.position_type == 3 or board_pos.position_type == 5:
        pen = get_pen_by_postiion(p_board, pos)
        if pen.animal_type == animal and pen.max_num > pen.current_num:
            pen.current_num += 1
            p_resource.resource_num += 1
            pen.save()
            p_resource.save()
        else:
            return Response({'error': 'You can\'t release animal in here'}, status=403)
    elif board_pos.position_type == 4:
        if board_pos.animal_num == 0:
            board_pos.animal_num += 1
            p_resource.resource_num += 1
            board_pos.save()
        else:
            return Response({'error': 'You can\'t release animal in here'}, status=403)
    else:
        return Response({'error': 'You can\'t release animal in here'}, status=403)

# 플레이어가 가진 직업이 하나도 없는지 체크
def is_first_job(player):
    cards = PlayerCard.objects.filter(player_id=player)
    card_ids = list(range(1,15))
    jobcards = cards.filter(card_id__in=card_ids)
    activated_jobs = jobcards.filter(activate=1)
    if not activated_jobs:
        return True
    return False