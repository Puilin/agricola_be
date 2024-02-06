from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync
from rest_framework.response import Response

class BroadcastMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # API 호출 시에 room_name이라는 필드가 요청에 있다면 추가
        room_num = request.GET.get('room_num')
        if room_num:
            request.room_num = room_num

        response = self.get_response(request)
        if room_num:
            self.broadcast(request, response)
        return response
    
    def broadcast(self, request, response):
        channel_layer = get_channel_layer()
        room_group_name = 'group_agricola%s' % request.GET['room_num'] # group_agricola1

        if isinstance(response, Response):
            json_response = json.dumps(response.data)
        else:
            # HttpResponseNotFound와 같은 다른 응답 형식에 대한 처리
            return

        async_to_sync(channel_layer.group_send)(room_group_name, {
            'type': 'api_response',
            'data': json_response
        })