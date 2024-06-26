from django.urls import path
from websocket import consumers
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    # 请求地址为ws:// + host + /ws/ + user_id + /message
    path('ws/<str:user_id>/message', consumers.ChatConsumer.as_asgi()),
    # path('ws/<str:user_id>/chat', consumers.ChatConsumer.as_asgi()),
]


application = ProtocolTypeRouter({
    # http请求使用这个
    "http": get_asgi_application(),

    # websocket请求使用这个
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})