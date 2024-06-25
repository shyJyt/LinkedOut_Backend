from enterprise.models import *
from user.models import User
from utils.qos import *
from utils.response import response
from utils.status_code import *
from utils.view_decorator import login_required, allowed_methods


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
        return response(code=PERMISSION, msg='您已经是企业用户')
    # 获取参数
    name = request.POST.get('name', None)
    intro = request.POST.get('intro', None)
    img = request.FILES.get('img', None)
    # 参数校验
    if not all([name, intro, img]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 使用qos对象存储上传图片
    img_url = 'enterprise/' + img.name
    # 先保存在本地Static文件夹
    with open('static/' + img_url, 'wb') as f:
        for chunk in img.chunks():
            f.write(chunk)
    # 上传到qos
    if not upload_file(img_url, 'static/' + img_url):
        return response(code=SERVER_ERROR, msg='上传图片失败')
    # 创建企业
    enterprise = Enterprise.objects.create(name=name, intro=intro, img_url=img_url)
    enterprise.save()
    # 关联企业管理员
    enterprise_user = EnterpriseUser.objects.create(user_id=user, enterprise_id=enterprise, role=0)
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
        return response(code=PERMISSION, msg='您已经是企业用户')
    # 获取参数
    enterprise_id = request.POST.get('enterprise_id', None)
    if not enterprise_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找企业
    enterprise = Enterprise.objects.filter(id=enterprise_id).first()
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    # 创建企业用户
    enterprise_user = EnterpriseUser.objects.create(user_id=user, enterprise_id=enterprise, role=1)
    enterprise_user.save()
    user.enterprise_user = enterprise_user
    user.save()
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
        return response(code=PERMISSION, msg='您不是企业用户')
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
        return response(code=PERMISSION, msg='您不是企业用户')
    # TODO 给企业管理员发送消息
    from_user_id = user.id
    enterprise = user.enterprise_user.enterprise
    # 找到企业管理员
    to_user_id = enterprise.enterpriseuser_set.filter(role=0).first().user_id
    content = '员工' + str(user.real_name) + '退出了企业'
    pass
    # 删除企业用户
    user.enterprise_user.delete()
    user.enterprise_user = None
    user.save()
    return response(msg='退出成功')
