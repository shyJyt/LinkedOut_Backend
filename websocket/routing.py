from django.urls import path

from websocket import consumers

websocket_urlpatterns = [
    # 请求地址为ws:// + host + /ws/ + user_id + /message
    path('ws/<str:user_id>/message', consumers.ChatConsumer.as_asgi()),
    # path('ws/<str:user_id>/chat', consumers.ChatConsumer.as_asgi()),
]