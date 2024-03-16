from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/(?P<room_name>\w+)/(?P<player_id>\w+)/", consumers.Consumer.as_asgi()),
]