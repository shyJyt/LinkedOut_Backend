from django.db import IntegrityError

from enterprise.models import Invitation, Transfer, PostRecruitment
from social.models import Message
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, login_required


def send_message(from_user, to_user, msg_type, obj_id, title, content):
    """
    发送系统通知（动态交互、员工变更等）
    :param : from_user, to_user, type, obj_id, title, content
    :return: 是否成功
    """
    try:
        message = Message(
            from_user=from_user,
            to_user=to_user,
            type=msg_type,
            obj_id=obj_id,
            title=title,
            content=content
        )
        message.save()
        return True
    except IntegrityError:
        return False


@allowed_methods(['GET'])
@login_required
def get_message_list(request):
    """
    获取用户消息列表
    :param request:
    :return: [code, msg, data]
    """
    user = request.user
    try:
        messages = Message.objects.filter(to_user=user).order_by('-create_time')
        message_list = []
        for message in messages:
            # is_handled默认为True
            is_handled = True
            # 查找是否处理,如果有obj_id
            if message.obj_id != '':
                # (5，'邀请'),(6，'转让'),(7'录用')
                if message.type == 5:
                    is_handled = Invitation.objects.get(id=message.obj_id).is_handled
                elif message.type == 6:
                    is_handled = Transfer.objects.get(id=message.obj_id).is_handled
                elif message.type == 7:
                    if user in PostRecruitment.objects.get(id=message.obj_id).accepted_user.all():
                        is_handled = False
                    else:
                        is_handled = True
            message_ele = {
                'from_user': message.from_user.nickname,
                'type': message.get_type_display(),
                'title': message.title,
                'content': message.content,
                'is_read': message.is_read,
                'create_time': message.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'obj_id': message.obj_id if message.obj_id else '',
                'is_handled': is_handled,
            }
            message_list.append(message_ele)
        return response(SUCCESS, '获取消息列表成功！', data=message_list)
    except Exception:
        return response(SERVER_ERROR, '获取消息列表失败！', error=True)


@allowed_methods(['GET'])
@login_required
def check_message(request):
    """
    查看消息详情
    :param request: message_id
    :return: [code, msg, data]
    """
    user = request.user
    message_id = request.GET.get('message_id')
    try:
        message = Message.objects.get(id=message_id)
        if message.to_user.id != user.id:
            return response(PARAMS_ERROR, '无查看权限！', error=True)
        message_detail = {
            'from_user': message.from_user.nickname,
            'type': message.get_type_display(),
            'obj_id': message.obj_id,
            'title': message.title,
            'content': message.content,
            'create_time': message.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if not message.is_read:
            message.is_read = True
            message.save()
        return response(SUCCESS, '查看消息详情成功！', data=message_detail)
    except Message.DoesNotExist:
        return response(PARAMS_ERROR, '消息不存在！', error=True)