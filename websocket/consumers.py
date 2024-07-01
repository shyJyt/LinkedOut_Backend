import datetime
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from enterprise.models import User
from social.models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket处理器
    继承自AsyncWebsocketConsumer,是一个异步处理器, 有两个重要属性:
    self.channel_name: 独一无二的长连接频道名,用于标识一个连接。
    self.channel_layer: 提供了 send(), group_send()和group_add() 3种方法,
    可以给单个频道或一个频道组发信息，还可以将一个频道加入到组。
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.mode = None
        self.user_id = None
        self.target_user_id = None

    async def connect(self):
        # 在建立连接时执行的操作
        # 可以在这里进行认证、建立会话等操作

        self.mode = self.scope['url_route']['kwargs'].get('mode', 'single')
        # 私聊
        if self.mode == 'chat':
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.target_user_id = self.scope['url_route']['kwargs']['target_user_id']
            # 生成私聊房间名，保证唯一性
            self.room_name = f'{min(self.user_id, self.target_user_id)}_{max(self.user_id, self.target_user_id)}'
            self.room_group_name = f'private_chat_{self.room_name}'
        # 消息通知
        else:
            user_id = self.scope['url_route']['kwargs']['user_id']
            # 每个用户的房间名用user_id标识
            self.room_name = user_id
            # 加入用户的系统组
            self.room_group_name = f'system_message_{user_id}'

        # 加入房间分组,一个用户一个组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 在断开连接时执行的操作
        # 可以在这里进行清理工作、关闭会话等操作
        # 离开房间分组
        # await 一个异步操作(必须是可异步的才能await) /
        # 因为这里定义为异步函数,所以可以直接await,如果定义为同步函数,需要使用async_to_sync包装
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 从websocket接收到消息时执行函数
    async def receive(self, text_data=None, bytes_data=None):
        # 处理接收到的消息
        # 可以在这里对接收到的消息进行处理，并根据需要执行相应的逻辑
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print(f"User ID: {self.user_id}")
        print(f"Target User ID: {self.target_user_id}")
        print(message)
        # 记录聊天内容
        if self.mode == 'chat':
            await self.save_chat_message(self.user_id, self.target_user_id, message)

        # 发送消息到分组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_message',
                'message': message,
                'obj_id': ''
            }
        )

    # 从频道组接收到消息后执行方法
    async def send_message(self, event):
        message = event['message']
        obj_id = event['obj_id']
        datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 发送消息到 WebSocket
        await self.send(text_data=json.dumps({
             'message': f'{datetime_str}:{message}',
             'obj_id': obj_id,
        }))

    @sync_to_async
    def save_chat_message(self, sender_id, receiver_id, message):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)
