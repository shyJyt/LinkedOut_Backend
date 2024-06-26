from enterprise.models import User, Enterprise, EnterpriseUser
from utils.qos import upload_file, get_file
from utils.response import response
from utils.status_code import PARAMS_ERROR, SERVER_ERROR, PERMISSION_ERROR
from utils.view_decorator import login_required, allowed_methods
from social.models import Message


@allowed_methods(['POST'])
@login_required
def createEnterprise(request):
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
    enterprise_user = EnterpriseUser.objects.create(user=user, enterprise=enterprise, role=0)
    enterprise_user.save()
    user.enterprise_user = enterprise_user
    user.save()
    return response(msg='创建成功')


@allowed_methods(['POST'])
@login_required
def joinEnterprise(request):
    """
    加入企业
    用户加入企业
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is not None:
        return response(code=PERMISSION_ERROR, msg='您已经是企业用户')
    # 获取参数
    enterprise_id = request.POST.get('enterprise_id', None)
    if not enterprise_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找企业
    enterprise = Enterprise.objects.filter(id=enterprise_id).first()
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    # 是否被邀请
    invitation = user.be_invited.filter(obj_id=enterprise_id, is_handled=False).first()
    if not invitation:
        return response(code=PERMISSION_ERROR, msg='您未被邀请')
    # 创建企业用户
    enterprise_user = EnterpriseUser.objects.create(enterprise=enterprise, role=1)
    enterprise_user.save()
    user.enterprise_user = enterprise_user
    user.save()
    # 处理邀请
    invitation.is_handled = True
    invitation.save()
    return response(msg='加入成功')


@allowed_methods(['POST'])
@login_required
def completeEnterpriseInfo(request):
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
def exitEnterprise(request):
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
        'from_user_id': user,
        'to_user_id': enterprise.enterpriseuser_set.filter(role=0).first().user,
        'type': 0,
        'title': '员工退出企业',
        'content': '员工' + str(user.real_name) + '退出了企业',
    }
    message = Message.objects.create(**message_params)
    message.save()
    return response(msg='退出成功')


@allowed_methods(['GET'])
@login_required
def getEEInfo(request):
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
            'id': employee.user.id,
            'position': employee.position,
            'work_age': employee.work_age,
            'img_url': employee_avatar_url,
        })
    data = {
        'enterprise_info': enterprise_info,
        'employee_list': employee_list,
    }
    return response(data=data)
