from .models import *
from .serializer import *
from rest_framework.response import Response
from .utils import *
from django.db.models import Q


def forest(player):
    forest_action = ActionBox.objects.get(id=11)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=1)
    # 숲에 누군가 있으면
    if forest_action.is_occupied:
        return Response({'detail': 'There\'s someone else in forest.'}, status=404)
    if forest_action.acc_resource > 0:
        # 숲에 이제 사람이 있음
        forest_action.is_occupied = True
        # 플레이어의 자원에 추가
        my_resource.resource_num = my_resource.resource_num + forest_action.acc_resource
        # 숲에서 나무를 몽땅 없앰
        forest_action.acc_resource -= forest_action.acc_resource

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
    # 흑집 -> 돌집
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
    sheep = PlayerResource.objects.filter(player_id=player).get(resource_id=7)

    # 양시장 이용 조건 체크
    cond1, cond2 = True, True
    # 양을 키울수 있는 공간이 있는지 체크
    if count_pens(board_pos) == 0:
        cond1 = False

    # 양을 식량으로 바꿀 수 있는 설비가 있는지 체크
    if not does_have_cooking_facility(player):
        cond2 = False

    if cond1 and cond2:
        sheep.resource_num += sheep_market_action.acc_resource
        sheep.save()
        sheep_market_action.acc_resource -= sheep_market_action.acc_resource
        sheep_market_action.save()
        return Response({"case": 1, "massege": "You can raise them(it) or cook them (it)"}, status=200)
    elif cond1:
        sheep.resource_num += sheep_market_action.acc_resource
        sheep.save()
        sheep_market_action.acc_resource -= sheep_market_action.acc_resource
        sheep_market_action.save()
        return Response({"case": 2, "massege": "You can raise them(it)"}, status=200)
    elif cond2:
        sheep.resource_num += sheep_market_action.acc_resource
        sheep.save()
        sheep_market_action.acc_resource -= sheep_market_action.acc_resource
        sheep_market_action.save()
        return Response({"case": 3, "massege": "You can cook them(it)"}, status=200)
    else:
        sheep_market_action.is_occupied = False
        sheep_market_action.save()
        return Response({"case": 0, "error": "You don't have neither pens nor main facilities for cooking"}, status=404)


def farm_extension(player):
    farm_ex_action = ActionBox.objects.get(id=8)
    if farm_ex_action.is_occupied:
        return Response({'detail': 'There\'s someone else in farm extension'}, status=404)

    resource = PlayerResource.objects.filter(player_id=player)

    tree = resource.get(resource_id=1)
    reed = resource.get(resource_id=3)
    soil = resource.get(resource_id=2)
    stone = resource.get(resource_id=4)

    board = PlayerBoardStatus.objects.get(player_id=player)

    can_build_cowshed = False
    if tree.resource_num >= 2:
        can_build_cowshed = True

    can_build_room = False
    # 나무집
    if (board.house_type == 0 and tree.resource_num >= 5 and reed.resource_num >= 2):
        can_build_room = True
    # 흙집
    if (board.house_type == 1 and soil.resource_num >= 5 and reed.resource_num >= 2):
        can_build_room = True
    # 돌집
    if (board.house_type == 2 and stone.resource_num >= 5 and reed.resource_num >= 2):
        can_build_room = True

    if can_build_cowshed and can_build_room:
        return Response({"code": 0, "message": "That player can build either cowshed or room"})
    if can_build_cowshed:
        return Response({"code": 1, "message": "That player can build only cowshed"})
    if can_build_room:
        return Response({"code": 2, "message": "That player can build only room"})
    return Response({'code': -1, "message": "That player doesn't seem to have enough resources"}, status=404)


def meeting_place(player):
    meeting_place_act = ActionBox.objects.get(id=9)
    if meeting_place_act.is_occupied:
        return Response({'detail': 'There\'s someone else in meeting place'}, status=404)

    meeting_place_act.is_occupied = True
    meeting_place_act.save()

    players = Player.objects.all()
    for p in players:
        p.fst_player = False
        p.save()
    player.fst_player = True
    player.save()

    return Response({'message': "The first player updated to player {}".format(player.id)})

# 23번 행동칸: 기본 가족 늘리기
def add_fam(player, card):
    add_fam_action = ActionBox.objects.get(id=23)
    my_board = PlayerBoardStatus.objects.get(player_id=player)
    player = Player.objects.get(id=player.id)
    my_subfac_card = PlayerCard.objects.filter(
        Q(player_id=player) &
        Q(activate=1) &
        Q(card_id__in=range(15, 29)))  # 29는 포함X
    target_card = PlayerCard.objects.get(card_id=22)
    activation_cost = ActivationCost.objects.get(card_id=22)
    my_resource = PlayerResource.objects.get(player_id=player, resource_id=1)

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
    # serializer = PlayerCardSerializer(my_subfac_card, many=True)
    # print("These are your subfacility cards. Choose one to activate.", serializer.data)
    # 고른 카드의 활성화 비용만큼 개인자원판에 있는지 확인
    # 살 수 있을만큼 자원 존재: 구입한 보조설비 카드가 활성화, 개인 자원판에서 activation cost만큼 차감한다
    if my_resource.resource_num >= activation_cost.resource_num:
        my_resource.resource_num -= activation_cost.resource_num
        target_card.activate = 1
    # 자원이 모자라 살 수 없는 경우 404
    else:
        return Response({'detail': 'There are not enough resources to buy this card.'}, status=404)

    response = Response({'success': 'Add family action completed successfully.'}, status=200)
    return response

def soil_mining(player):
    soil_action = ActionBox.objects.get(id=13)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=2)
    # 흙채굴장에 누군가 있으면
    if soil_action.is_occupied:
        return Response({'detail': 'There\'s someone else in soil mining farm.'}, status=404)
    if soil_action.acc_resource > 0:
        # 흙채굴장에 이제 사람이 있음
        soil_action.is_occupied = True
        # 플레이어의 자원에 추가
        my_resource.resource_num += soil_action.acc_resource
        # 흙채굴장에서 흙를 몽땅 없앰
        soil_action.acc_resource -= soil_action.acc_resource

        # db에 저장
        soil_action.save()
        my_resource.save()

        serializer = PlayerResourceSerializer(my_resource)
        return Response(serializer.data)
    else:
        return Response({'detail': 'There\'s no exisiting resources.'}, status=404)

def reed_field(player):
    reed_action = ActionBox.objects.get(id=14)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=3)
    # 갈대밭에 누군가 있으면
    if reed_action.is_occupied:
        return Response({'detail': 'There\'s someone else in reed field.'}, status=404)
    if reed_action.acc_resource > 0:
        # 갈대밭에 이제 사람이 있음
        reed_action.is_occupied = True
        # 플레이어의 자원에 추가
        my_resource.resource_num = my_resource.resource_num + reed_action.acc_resource
        # 같대밭에서 갈대를 몽땅 없앰
        reed_action.acc_resource -= reed_action.acc_resource

        # db에 저장
        reed_action.save()
        my_resource.save()

        serializer = PlayerResourceSerializer(my_resource)
        return Response(serializer.data)
    else:
        return Response({'detail': 'There\'s no exisiting resources.'}, status=404)
    
    
def day_laborer(player):
    day_action = ActionBox.objects.get(id=15)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=10)
    # 날품팔이에 누군가 있으면
    if day_action.is_occupied:
        return Response({'detail': 'There\'s someone else in day laborer.'}, status=404)
    
    # 날품팔이에 이제 사람이 있음
    day_action.is_occupied = True
    # 플레이어의 자원에 추가
    my_resource.resource_num += 2

    # db에 저장
    day_action.save()
    my_resource.save()

    serializer = PlayerResourceSerializer(my_resource)
    return Response(serializer.data)

def fishing(player):
    fishing_action = ActionBox.objects.get(id=16)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=10)
    # 낚시에 누군가 있으면
    if fishing_action.is_occupied:
        return Response({'detail': 'There\'s someone else in fishing.'}, status=404)
    if fishing_action.acc_resource > 0:
        # 낚시에 이제 사람이 있음
        fishing_action.is_occupied = True
        # 플레이어의 자원에 추가
        my_resource.resource_num = my_resource.resource_num + fishing_action.acc_resource
        # 낚시에서 음식을 몽땅 없앰
        fishing_action.acc_resource -= fishing_action.acc_resource

        # db에 저장
        fishing_action.save()
        my_resource.save()

        serializer = PlayerResourceSerializer(my_resource)
        return Response(serializer.data)
    else:
        return Response({'detail': 'There\'s no exisiting resources.'}, status=404)
    
def west_mine(player):
    west_action = ActionBox.objects.get(id=22)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=4)
    # 서부채석장에 누군가 있으면
    if west_action.is_occupied:
        return Response({'detail': 'There\'s someone else in west mine.'}, status=404)
    if west_action.acc_resource > 0:
        # 서부채석장에 이제 사람이 있음
        west_action.is_occupied = True
        # 플레이어의 자원에 추가
        my_resource.resource_num = my_resource.resource_num + west_action.acc_resource
        # 서부채석장에서 돌을 몽땅 없앰
        west_action.acc_resource -= west_action.acc_resource

        # db에 저장
        west_action.save()
        my_resource.save()

        serializer = PlayerResourceSerializer(my_resource)
        return Response(serializer.data)
    else:
        return Response({'detail': 'There\'s no exisiting resources.'}, status=404)
    
def east_mine(player):
    east_action = ActionBox.objects.get(id=27)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=4)
    # 동부채석장에 누군가 있으면
    if east_action.is_occupied:
        return Response({'detail': 'There\'s someone else in east mine.'}, status=404)
    if east_action.acc_resource > 0:
        # 동부채석장에 이제 사람이 있음
        east_action.is_occupied = True
        # 플레이어의 자원에 추가
        my_resource.resource_num = my_resource.resource_num + east_action.acc_resource
        # 동부채석장에서 돌을 몽땅 없앰
        east_action.acc_resource -= east_action.acc_resource

        # db에 저장
        east_action.save()
        my_resource.save()

        serializer = PlayerResourceSerializer(my_resource)
        return Response(serializer.data)
    else:
        return Response({'detail': 'There\'s no exisiting resources.'}, status=404)
    
def vege_seed(player):
    vege_action = ActionBox.objects.get(id=25)
    my_resource = PlayerResource.objects.filter(player_id=player).get(resource_id=6)
    # 채소종자에 누군가 있으면
    if vege_action.is_occupied:
        return Response({'detail': 'There\'s someone else in vege seed.'}, status=404)
    
    # 채소종자에 이제 사람이 있음
    vege_action.is_occupied = True
    vege_action.save()
    # 플레이어의 자원에 추가
    my_resource.resource_num += 1

    # db에 저장
    
    my_resource.save()

    serializer = PlayerResourceSerializer(my_resource)
    return Response(serializer.data)

def facility(player, card):
    facility_action = ActionBox.objects.get(id=20)
    active_costs = ActivationCost.objects.filter(card_id = card)
    for active_cost in active_costs:
            my_resource = PlayerResource.objects.get(player_id=player.id, resource_id=active_cost.resource_id)
            if my_resource.resource_num < active_cost.resource_num:
                return Response({'detail': 'Not enough resources'}, status=404)
    if 29 <= card.id <= 38:
        active_card = MainFacilityCard.objects.get(card_id=card.id)
        active_costs = ActivationCost.objects.filter(card_id=card)
        if active_card.player_id != 0:
            return Response({'detail': 'This card has its owner'}, status=404)
        for active_cost in active_costs:
            my_resource = PlayerResource.objects.get(player_id=player.id, resource_id=active_cost.resource_id)
            my_resource.resource_num -= active_cost.resource_num
            my_resource.save()
        facility_action.is_occupied = True
        facility_action.save()
        active_card.player_id = player.id
        active_card.save()
        PlayerCard.objects.create(activate=1, player_id=player, card_id=active_card.card_id)
        return Response({'message': 'Activate Success'})
    elif 15 <= card.id <= 28:
        active_card = PlayerCard.objects.get(card_id=card.id)
        if active_card.player_id != player:
            return Response({'detail': 'This is not your card'}, status=404)
        active_costs = ActivationCost.objects.filter(card_id=card)
        for active_cost in active_costs:
            my_resource = PlayerResource.objects.get(player_id=player.id, resource_id=active_cost.resource_id)
            my_resource.resource_num -= active_cost.resource_num
            my_resource.save()
        facility_action.is_occupied = True
        facility_action.save()
        active_card.activate = 1
        active_card.save()
        return Response({'message': 'Activate Success'})
    else:
        return Response({'detail': 'This is not faility card'}, status=404)
    
def baking(player, card_id):
    baking_action = ActionBox.objects.get(id = 19)
    my_grain = PlayerResource.objects.get(player_id = player.id, resource_id = 5)
    my_food =PlayerResource.objects.get(player_id = player.id, resource_id = 10)
    if does_have_baking_facility(player) == False:
        return Response({'detail': 'You don\'t have faility card'}, status=404)
    if baking_action.is_occupied:
        return Response({'detail': 'There\'s someone else in baking.'}, status=404)
    if my_grain.resource_num == 0:
        return Response({'detail': 'You don\'t have grain'}, status=404)
    
    cook_num = card_id
    facility_cards = MainFacilityCard.objects.filter(player_id = player.id)
    #흙가마
    if cook_num > 0:
        try:
            facility_card = PlayerCard.objects.get(player_id = player.id, card_id = 33)
            cook_num -= 1
            my_grain.resource_num -= 1
            my_food.resource_num += 5
        except PlayerCard.DoesNotExist:
            pass

    #돌가마
    if cook_num > 0:
        try:
            facility_card = PlayerCard.objects.get(player_id = player.id, card_id = 34)
            for _ in range(2):
                if cook_num == 0: break
                cook_num -= 1
                my_grain.resource_num -= 1
                my_food.resource_num += 4
        except PlayerCard.DoesNotExist:
            pass

    for facility_card in facility_cards:
        #화덕
        if facility_card.card_id in [31, 32]:
            my_grain.resource_num -= cook_num
            my_food.resource_num += cook_num*3
            cook_num = 0
        
        #화로
        if facility_card.card_id in [29, 30]:
            my_grain.resource_num -= cook_num
            my_food.resource_num += cook_num*2
            cook_num = 0

    if cook_num != 0:
        return Response({'detail': 'You can\'t bake the required amount of bread.'}, status=404)

    baking_action.is_occupied = True
    baking_action.save()
    my_food.save()
    my_grain.save()

    return Response({'message': 'baking Success'})

def lesson(player, card):
    lesson_act = ActionBox.objects.get(id=5)
    if lesson_act.is_occupied:
        return Response({'detail': 'There\'s someone else in lesson'}, status=404)
    
    cards = PlayerCard.objects.filter(player_id=player)
    card_ids = list(range(1, 15))
    jobcards = cards.filter(card_id__in=card_ids)
    food = PlayerResource.objects.get(player_id=player, resource_id=10)

    # 첫직업은 무료
    if is_first_job(player):
        try:
            job = jobcards.get(card_id=card)
            job.activate = 1
            job.save()
            lesson_act.is_occupied = True
            lesson_act.save()
            serialier = PlayerCardSerializer(job)
            return Response({'message':"Player {} got a job".format(player.id), "job":serialier.data})
        except AttributeError:
            return Response({'error': 'Invalid card id : Check it if you have'}, status=404)
    else:
        if food.resource_num < 1:
            return Response({'error': 'That player seems not to have enough food'}, status=404)
        try:
            job = jobcards.get(card_id=card)
            job.activate = 1
            job.save()
            lesson_act.is_occupied = True
            lesson_act.save()
            food.resource_num -= 1
            food.save()
            serialier = PlayerCardSerializer(job)
            return Response({'message':"Player {} got a job".format(player.id), "job":serialier.data})
        except AttributeError:
            return Response({'error': 'Invalid card id : Check it if you have'}, status=404)