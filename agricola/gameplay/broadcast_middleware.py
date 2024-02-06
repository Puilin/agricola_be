from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync

class BroadcastMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # API 호출 시에 room_name이라는 필드가 요청에 있다면 추가
        room_num = request.GET['room_num']
        if room_num:
            request.room_num = room_num

        response = self.get_response(request)
        if room_num:
            self.broadcast(request, response)
        return response
    
    def broadcast(request, response):
        channel_layer = get_channel_layer()
        room_group_name = 'group_agricola%s' % request.query_params.get('room_num') # group_agricola1

        json_response = json.dumps(response.data)

        async_to_sync(channel_layer.group_send)(room_group_name, {
            'type': 'api_response',
            'data': json_response
        })