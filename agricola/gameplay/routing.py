from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    #re_path(r"ws/(?P<room_name>\w+)/(?P<player_id>\w+)/$", consumers.Consumer.as_asgi()),
    path("ws/<str:room_name>/<str:player_id>/", consumers.Consumer.as_asgi())
]