class RoomInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # API 호출 시에 room_name이라는 필드가 요청에 있다면 추가
        room_num = request.GET['room_num']
        if room_num:
            request.room_num = room_num

        response = self.get_response(request)
        return response