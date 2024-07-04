from enterprise.models import User, Enterprise, EnterpriseUser, Invitation
from utils.qos import upload_file, get_file
from utils.response import response
from utils.status_code import PARAMS_ERROR, SERVER_ERROR, PERMISSION_ERROR, MYSQL_ERROR
from utils.view_decorator import login_required, allowed_methods
from social.models import Message
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@allowed_methods(['POST'])
@login_required
def create_enterprise(request):
    """
    创建企业
    用户创建企业时，需填写企业名称、简介、图片等
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is not None:
        return response(code=PERMISSION_ERROR, msg='您已经是企业用户')
    # 获取参数
    name = request.POST.get('name', None)
    intro = request.POST.get('intro', None)
    img = request.FILES.get('img', None)
    # 参数校验
    if not all([name, intro, img]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 使用qos对象存储上传图片
    img_key = 'enterprise_' + str(user.id) + '_' + img.name
    # 先保存在本地Static文件中
    # 输出当前路径
    with open('./Static/' + img_key, 'wb') as f:
        for chunk in img.chunks():
            f.write(chunk)
    # 上传到qos
    if not upload_file(img_key, 'Static/' + img_key):
        return response(code=SERVER_ERROR, msg='上传图片失败')
    # 上传成功,删除本地文件
    import os
    os.remove('./Static/' + img_key)
    # 创建企业
    enterprise = Enterprise.objects.create(name=name, intro=intro, img_url=img_key)
    enterprise.save()
    # 关联企业管理员
    enterprise_user = EnterpriseUser.objects.create(enterprise=enterprise, role=0)
    enterprise_user.save()
    user.enterprise_user = enterprise_user
    user.save()
    return response(msg='创建成功')


@allowed_methods(['POST'])
@login_required
def join_enterprise(request):
    """
    加入企业
    用户加入企业
    """
    user = request.user
    user: User
    # 获取参数
    invitation_id = request.POST.get('invitation_id', None)
    action = request.POST.get('action', None)
    if not all([invitation_id, action]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找对应邀请
    invitation = user.be_invited.filter(id=invitation_id, is_handled=False).first()
    if not invitation:
        return response(code=MYSQL_ERROR, msg='您没有未处理的对应邀请')
    # action 1 为接受, 0 为拒绝
    if action not in ['1', '0']:
        return response(code=PARAMS_ERROR, msg='参数错误')
    if action == '1':
        # 查看用户是否为企业用户
        if user.enterprise_user is not None:
            return response(code=PERMISSION_ERROR, msg='您已经是企业用户')
        invitation: Invitation
        enterprise = invitation.from_user.enterprise_user.enterprise
        if not enterprise:
            return response(code=MYSQL_ERROR, msg='对应公司不存在')
        # 创建企业用户
        enterprise_user = EnterpriseUser.objects.create(enterprise=enterprise, role=1)
        enterprise_user.save()
        user.enterprise_user = enterprise_user
        user.save()
        # 处理邀请
        invitation.is_handled = True
        invitation.save()
        # 将现有的邀请全部处理
        for invitation in user.be_invited.filter(is_handled=False):
            invitation.is_handled = True
            invitation.save()
    elif action == '0':
        invitation.is_handled = True
        invitation.save()
    # 给邀请人发送消息
    content = '员工' + str(user.real_name) + ('接受' if action == '1' else '拒绝') + '了您的邀请'
    message_params = {
        'from_user': user,
        'to_user': invitation.from_user,
        'type': 0,
        'title': '企业邀请结果',
        'content': content,
        'obj_id': invitation.id
    }
    message = Message.objects.create(**message_params)
    message.save()
    # 提醒邀请人有新消息
    room_group_name = f'system_message_{invitation.from_user.id}'
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'send_message',
            'message': content,
            'obj_id': invitation.id
        }
    )
    return response(msg='处理成功')


@allowed_methods(['POST'])
@login_required
def complete_enterprise_info(request):
    """
    完善信息
    企业用户完善企业信息,如工龄、岗位等
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None:
        return response(code=PERMISSION_ERROR, msg='您不是企业用户')
    # 获取参数
    position = request.POST.get('position', None)
    work_age = request.POST.get('work_age', None)
    phone_number = request.POST.get('phone_number', None)
    # 不为空则更新对应字段
    if position:
        user.enterprise_user.position = position
    if work_age:
        user.enterprise_user.work_age = work_age
    if phone_number:
        user.enterprise_user.phone_number = phone_number
    user.enterprise_user.save()
    return response(msg='完善成功')


@allowed_methods(['POST'])
@login_required
def exit_enterprise(request):
    """
    退出企业
    用户退出企业
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None:
        return response(code=PERMISSION_ERROR, msg='您不是企业用户')
    # 查看是否为企业管理员
    if user.enterprise_user.role == 0:
        return response(code=PERMISSION_ERROR, msg='您是企业管理员,不能退出企业')
    # 删除企业用户
    enterprise = user.enterprise_user.enterprise
    user.enterprise_user.delete()
    user.enterprise_user = None
    user.save()
    # 给企业管理员发送消息
    message_params = {
        'from_user': user,
        'to_user': enterprise.enterpriseuser_set.filter(role=0).first().user,
        'type': 0,
        'title': '员工退出企业',
        'content': '员工' + str(user.real_name) + '退出了企业',
    }
    message = Message.objects.create(**message_params)
    message.save()
    # 提醒管理员有新消息
    manager_id = enterprise.enterpriseuser_set.filter(role=0).first().user.id
    room_group_name = f'system_message_{manager_id}'

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'send_message',
            'message': f'员工{user.real_name}退出企业'
        }
    )

    return response(msg='退出成功')


@allowed_methods(['GET'])
@login_required
def get_ee_info(request):
    """
    获取企业信息和员工列表
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None:
        return response(code=PERMISSION_ERROR, msg='您不是企业用户')
    enterprise = user.enterprise_user.enterprise
    # 获取企业icon等信息
    enterprise: Enterprise
    enterprise_img_key = enterprise.img_url
    enterprise_img_url = get_file(enterprise_img_key)
    if enterprise_img_url == '':
        return response(code=SERVER_ERROR, msg='获取图片失败')
    enterprise_info = {
        'id': enterprise.id,
        'name': enterprise.name,
        'img_url': enterprise_img_url,
        'intro': enterprise.intro,
    }
    # 获取企业员工列表
    employee_list = []
    for employee in enterprise.enterpriseuser_set.all():
        # 获取员工头像等信息
        employee: EnterpriseUser
        employee_user = employee.user
        employee_user: User
        employee_avatar_key = employee_user.avatar_key
        employee_avatar_url = get_file(employee_avatar_key)
        employee_list.append({
            'id': employee.id,
            'real_name': employee.user.real_name,
            'position': employee.position,
            'work_age': employee.work_age,
            'img_url': employee_avatar_url,
        })
    data = {
        'enterprise_info': enterprise_info,
        'employee_list': employee_list,
    }
    return response(data=data)


@allowed_methods(['POST'])
@login_required
def accept_transfer(request):
    """
    接受管理员权限转让
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 1:
        return response(code=PERMISSION_ERROR, msg='您不是企业员工')
    # 获取参数
    transfer_id = request.POST.get('transfer_id', None)
    action = request.POST.get('action', None)
    if not all([transfer_id, action]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找对应未处理的转让邀请
    transfer = user.be_transferred.filter(id=transfer_id, is_handled=False).first()
    if not transfer:
        return response(code=MYSQL_ERROR, msg='您没有未处理的对应邀请')
    if action not in ['1', '0']:
        return response(code=PARAMS_ERROR, msg='参数错误')
    new_manager = user.enterprise_user
    if (not new_manager or new_manager.role != 1 or
            new_manager.enterprise != transfer.from_user.enterprise_user.enterprise):
        return response(code=MYSQL_ERROR, msg='您不是对应企业员工')
    if action == '1':
        # 更新企业新管理员
        new_manager.role = 0
        new_manager.save()
        # 更改原管理员信息
        original_manager = transfer.from_user.enterprise_user
        original_manager.role = 1
        original_manager.save()
        # 处理转让
        transfer.is_handled = True
        transfer.save()
    else:
        # 拒绝转让
        transfer.is_handled = True
        transfer.save()
    content = '员工' + str(user.real_name) + ('接受' if action == '1' else '拒绝') + '了您的管理员权限'
    # 给原管理员发送消息
    message_params = {
        'from_user': user,
        'to_user': transfer.from_user,
        'type': 0,
        'title': '管理员权限转让',
        'content': content,
        'obj_id': transfer.id
    }
    message = Message.objects.create(**message_params)
    message.save()
    # 提醒原管理员有新消息
    manager_id = transfer.from_user.id
    room_group_name = f'system_message_{manager_id}'
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'send_message',
            'message': content,
            'obj_id': transfer.id
        }
    )
    # 将现有的管理员权限转让消息全部处理
    for transfer in user.be_transferred.filter(is_handled=False):
        transfer.is_handled = True
        transfer.save()
    return response(msg='处理成功')
