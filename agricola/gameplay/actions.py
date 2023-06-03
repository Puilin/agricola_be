from .models import *
from .serializer import *
from rest_framework.response import Response

def forest(player):
    forest_action = ActionBox.objects.get(id=11)
    my_resource = PlayerResource.objects.get(player_id=player.id, resource_id=1)
    # 숲에 누군가 있으면
    if forest_action.is_occupied:
        return Response({'detail': 'There\'s someone else in forest.'}, status=404)
    if forest_action.acc_resource > 0:
        # 숲에 이제 사람이 있음
        forest_action.is_occupied = True
        # 숲에서 나무 3개 없앰
        forest_action.acc_resource -= 3
        forest_action.save()
        # 플레이어의 자원에 추가
        my_resource.resource_num += 3
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
    my_resource.save()

    serializer = PlayerResourceSerializer(my_resource)
    return Response(serializer.data)