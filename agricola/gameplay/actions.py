from .models import *
from .serializer import *
from rest_framework.response import Response

def forest(player):
    forest_action = ActionBox.objects.get(id=11)
    my_resource = PlayerResource.objects.get(player_id=player.id, resource_id=1)
    if forest_action.acc_resource > 0:
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