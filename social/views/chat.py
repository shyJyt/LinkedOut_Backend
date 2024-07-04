from django.db.models import Q

from enterprise.models import User
from social.models import ChatMessage
from utils.qos import get_file
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, login_required


@allowed_methods(['GET'])
@login_required
def get_chat_history(request):
    """
    获取聊天记录列表
    :param request:
    :return: [code, msg, data]
    """
    user = request.user
    user_id = request.GET.get('user_id')
    if not user_id:
        return response(PARAMS_ERROR, '请选择正确的私信用户', error=True)
    if user.id == int(user_id):
        return response(PARAMS_ERROR, '不能向自己发私信！', error=True)
    try:
        chat_history = ChatMessage.objects.filter(
            Q(sender=user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=user)
        ).order_by('timestamp')
        history_list = list(chat_history.values('sender_id', 'receiver_id', 'message', 'timestamp'))
        for message in history_list:
            message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return response(MYSQL_ERROR, str(e), error=True)

    return response(SUCCESS, '消息记录获取成功！', data=history_list)


@allowed_methods(['GET'])
@login_required
def get_chat_users(request):
    """
    获取聊天记录列表
    :param request:
    :return: [code, msg, data]
    """
    user = request.user
    try:
        chat_users = User.objects.filter(
            Q(sent_messages__receiver=user) |
            Q(received_messages__sender=user)
        ).distinct()
    except Exception as e:
        return response(MYSQL_ERROR, str(e), error=True)

    users_list = []
    for user in chat_users:
        user_info = {
            'id': user.id,
            'nickname': user.nickname,
            'avatar': get_file(user.avatar_key),
        }
        users_list.append(user_info)

    return response(SUCCESS, '获取聊天用户成功！', data=users_list)

