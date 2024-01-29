"""
ASGI config for agricola project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agricola.settings')
import django
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from gameplay.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
  "websocket": AuthMiddlewareStack(
    URLRouter(
      websocket_urlpatterns
    )
  )
})