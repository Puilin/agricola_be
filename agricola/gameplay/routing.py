from django.urls import path

from . import consumers

# ws://localhost:8000/ws/agricola1/player_1/
websocket_urlpatterns = [
        path('ws/<str:room_name>/player_<str:player_id>/', consumers.Consumer.as_asgi())
]
