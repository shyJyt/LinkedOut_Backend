from django.db import IntegrityError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from enterprise.models import User, Enterprise
from social.views.message import send_message
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, login_required


@allowed_methods(['POST'])
@login_required
def follow_user(request):
    """
    关注用户/取消关注
    :param request: user_id
    :return: [code, msg]
    """
    user = request.user
    user_id = request.POST.get('user_id')
    try:
        user_id = int(user_id)
    except ValueError:
        return response(PARAMS_ERROR, '无效的用户ID！', error=True)
    if user_id == user.id:
        return response(PARAMS_ERROR, '用户不能关注自己！', error=True)
    try:
        following = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response(PARAMS_ERROR, '该用户不存在！', error=True)
    if following in user.follow_user.all():
        user.follow_user.remove(following)
        msg = '取消关注！'
    else:
        user.follow_user.add(following)
        msg = '关注成功！'
        send_message(user, following, 4, user.id, '关注', f'用户 {user.nickname} 开始关注你啦！')
        # 给被点赞的用户发送消息
        followed_id = following.id
        group_room_name = f'system_message_{followed_id}'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_room_name,
            {
                'type': 'send_message',
                'message': f'用户 {user.nickname} 开始关注你啦！',
            }
        )
    user.save()
    return response(SUCCESS, msg)


@allowed_methods(['POST'])
@login_required
def follow_enterprise(request):
    """
    关注企业
    :param request: enterprise_id
    :return: [code, msg]
    """
    user = request.user
    enter_id = request.POST.get('enterprise_id')
    try:
        following = Enterprise.objects.get(id=enter_id)
    except Enterprise.DoesNotExist:
        return response(PARAMS_ERROR, '该企业不存在！', error=True)
    if following in user.follow_enterprise.all():
        user.follow_enterprise.remove(following)
        msg = '取消关注！'
    else:
        user.follow_enterprise.add(following)
        msg = '关注成功！'
    user.save()
    return response(SUCCESS, msg)