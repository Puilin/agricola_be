from django.urls import path

from . import consumers
from channels.routing import ProtocolTypeRouter, URLRouter

websocket_urlpatterns = [
    path('chat/<str:room_name>/', consumers.GameConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(websocket_urlpatterns)
    }
)
