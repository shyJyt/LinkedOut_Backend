
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from websocket.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    # "http": django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            # 后面会完善
            websocket_urlpatterns
        )
    ),
})
