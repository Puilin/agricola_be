from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    #re_path(r"ws/(?P<room_name>\w+)/(?P<player_id>\w+)/$", consumers.Consumer.as_asgi()),
    re_path(r"ws/", consumers.Consumer.as_asgi()),
]