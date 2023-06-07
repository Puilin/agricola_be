from django.urls import path

from . import consumers
from channels.routing import ProtocolTypeRouter, URLRouter

websocket_urlpatterns = [
    path('ws/room_<str:room_name>/player_<str:player_id>/', consumers.GameConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(websocket_urlpatterns)
    }
)
