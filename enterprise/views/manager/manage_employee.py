from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from enterprise.models import EnterpriseUser, User, Invitation
from social.models import Message
from utils.response import response
from utils.status_code import *
from utils.view_decorator import login_required, allowed_methods


@allowed_methods(['POST'])
@login_required
def add_employee(request):
    """
    添加员工
    企业管理员添加员工
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    # 获取参数
    user_id = request.POST.get('user_id', None)
    if not user_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找用户
    employee = User.objects.filter(id=user_id).first()
    if not employee:
        return response(code=PARAMS_ERROR, msg='用户不存在')
    # 不能邀请自己
    if employee == user:
        return response(code=PERMISSION_ERROR, msg='你不能邀请自己')
    # 创建邀请
    invitation_params = {
        'from_user': user,
        'to_user': employee,
        'obj_id': user.enterprise_user.enterprise.id,
    }
    invitation = Invitation.objects.create(**invitation_params)
    invitation.save()
    # 发送消息
    message_params = {
        'from_user': user,
        'to_user': employee,
        'type': 0,
        'title': '邀请加入企业',
        'content': '管理员邀请你加入企业' + str(user.enterprise_user.enterprise.name),
        'obj_id': invitation.id,
    }
    message = Message.objects.create(**message_params)
    message.save()

    # 给被邀请的用户发送消息
    employee_id = employee.id
    channel_layer = get_channel_layer()
    group_room_name = f'system_message_{employee_id}'
    async_to_sync(channel_layer.group_send)(
        group_room_name,
        {
            'type': 'send_message',
            'message': '管理员邀请你加入企业' + str(user.enterprise_user.enterprise.name),
            'obj_id': invitation.id
        }
    )

    return response(msg='邀请成功')


@allowed_methods(['POST'])
@login_required
def expel_employee(request):
    """
    开除员工
    企业管理员开除员工
    """
    user = request.user
    user: User
    # 查看用户是否为企业管理员
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    # 获取参数
    employee_id = request.POST.get('employee_id', None)
    if not employee_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找用户
    employee = user.enterprise_user.enterprise.enterpriseuser_set.filter(id=employee_id).first()
    if not employee:
        return response(code=PARAMS_ERROR, msg='员工不存在')
    # 看是否是自己
    if employee == user.enterprise_user:
        return response(code=PERMISSION_ERROR, msg='您不能开除自己')
    # 删除企业用户
    employee_user = employee.user
    employee.delete()
    employee_user.enterprise_user = None
    employee_user.save()
    # 发送消息,必须在删除之后,否则消息会被级联删除（很奇怪）
    message_params = {
        'from_user': user,
        'to_user': employee_user,
        'type': 0,
        'title': '开除通知',
        'content': '管理员开除了你',
    }
    message = Message.objects.create(**message_params)
    message.save()

    # 给被开除的用户发送消息
    employee_id = employee_user.id
    group_room_name = f'system_message_{employee_id}'
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_room_name,
        {
            'type': 'send_message',
            'message': '您被开除了'
        }
    )
    return response(msg='开除成功')
