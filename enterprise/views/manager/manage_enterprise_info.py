from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from enterprise.models import User, Transfer
from social.models import Message
from utils.qos import upload_file
from utils.response import response
from utils.status_code import PERMISSION_ERROR, PARAMS_ERROR, SERVER_ERROR, MYSQL_ERROR
from utils.view_decorator import login_required, allowed_methods


@allowed_methods(['POST'])
@login_required
def update_enterprise_info(request):
    """
    企业管理员可修改企业信息,如名称、简介、图片等
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    # 获取参数
    intro = request.POST.get('intro', None)
    img = request.FILES.get('img', None)
    # 查找企业
    enterprise = user.enterprise_user.enterprise
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    # 更新字段
    if intro:
        enterprise.intro = intro
    if img:
        img_url = 'enterprise' + str(user.id) + img.name
        with open('Static/' + img_url, 'wb') as f:
            for chunk in img.chunks():
                f.write(chunk)
        if not upload_file(img_url, 'Static/' + img_url):
            # 删除本地文件
            import os
            os.remove('Static/' + img_url)
            return response(code=SERVER_ERROR, msg='上传图片失败')
        # 删除本地文件
        import os
        os.remove('Static/' + img_url)
        enterprise.img_url = img_url
    enterprise.save()
    return response(msg='修改成功')


@allowed_methods(['POST'])
@login_required
def transfer_manager(request):
    """
    企业管理员可转让管理员权限
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    # 获取参数
    new_manager_id = request.POST.get('new_manager_id', None)
    if not new_manager_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找新管理员
    new_manager = user.enterprise_user.enterprise.enterpriseuser_set.filter(id=new_manager_id).first()
    if not new_manager:
        return response(code=MYSQL_ERROR, msg='目标员工不存在')
    # 检查是否是自己
    if new_manager == user.enterprise_user:
        return response(code=PARAMS_ERROR, msg='不能转让给自己')
    # 转让管理员权限
    # 记录转让
    transfer_params = {
        'from_user': user,
        'to_user': new_manager.user,
        'obj_id': new_manager.enterprise.id,
    }
    transfer = Transfer.objects.create(**transfer_params)
    transfer.save()
    # 给目标员工发送消息
    message_params = {
        'from_user': user,
        'to_user': new_manager.user,
        'title': '企业管理员权限转让消息',
        'content': '您收到了一条企业管理员权限转让消息',
        'type': 6,
        'obj_id': transfer.id
    }
    message = Message(**message_params)
    message.save()
    # 给目标员工用户发送系统消息
    employee_id = new_manager.user.id
    group_room_name = f'system_message_{employee_id}'
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_room_name,
        {
            'type': 'send_message',
            'message': '您收到了一条企业管理员权限转让消息',
            'obj_id': transfer.id
        }
    )
    return response(msg='发起转让成功')
