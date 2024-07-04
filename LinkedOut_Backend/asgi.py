"""
ASGI config for LinkedOut_Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import django

from channels.routing import get_default_application


django.setup()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LinkedOut_Backend.settings")

application = get_default_application()

# application = ProtocolTypeRouter({
#     # http请求使用这个
#     "http": get_asgi_application(),
#
#     # websocket请求使用这个
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })
