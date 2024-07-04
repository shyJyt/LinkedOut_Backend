from django.urls import path

from websocket import consumers

websocket_urlpatterns = [
    # 请求地址为ws:// + host + /ws/ + user_id + /message
    path('ws/<str:user_id>/message', consumers.ChatConsumer.as_asgi(), {'mode': 'single'}),
    # path('ws/<str:user_id>/chat', consumers.ChatConsumer.as_asgi()),
    # mode=single 表示单向消息发送，mode=chat 表示私聊
    path('ws/chat/<str:user_id>/<str:target_user_id>', consumers.ChatConsumer.as_asgi(), {'mode': 'chat'}),
    path('ws/new_chat/<str:user_id>', consumers.ChatConsumer.as_asgi(), {'mode': 'newchat'})
]

