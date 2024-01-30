from django.urls import path, re_path

from . import consumers

# ws://localhost:8000/ws/agricola1/player_1/
websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/player_(?P<player_id>\w+)/', consumers.Consumer.as_asgi())
]
