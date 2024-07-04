from enterprise.models import Enterprise, EnterpriseUser, User
from utils.qos import get_file
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, guest_and_user


@allowed_methods(['GET'])
def search_enterprise(request):
    """
    搜索企业
    用户搜索企业
    """
    name = request.GET.get('name', None)
    if not name:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    enterprise = Enterprise.objects.filter(name__contains=name)
    data = []
    for e in enterprise:
        img_key = e.img_url
        img_url = get_file(img_key)
        data.append({
            'id': e.id,
            'name': e.name,
            'intro': e.intro,
            'img_url': img_url
        })
    return response(data=data)


@allowed_methods(['GET'])
@guest_and_user
def get_enterprise_info(request):
    """
    获取企业信息
    用户查看企业信息
    """
    enterprise_id = request.GET.get('enterprise_id', None)
    if not enterprise_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    enterprise = Enterprise.objects.filter(id=enterprise_id).first()
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    img_key = enterprise.img_url
    img_url = get_file(img_key)
    # 获取企业员工列表,企业管理员排在第一位
    employee_list = []
    for employee in enterprise.enterpriseuser_set.all().order_by('role'):
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
    # 获取企业信息
    enterprise_info = {
        'name': enterprise.name,
        'intro': enterprise.intro,
        'img_url': img_url,
        'is_follow': False,
    }
    # 用户关注情况
    user = request.user
    if user and user.follow_enterprise.filter(id=enterprise.id).exists():
        enterprise_info['is_follow'] = True  # 如果用户已登录且关注企业，is_follow=True
    data = {
        'enterprise_info': enterprise_info,
        'employee_list': employee_list,
    }
    return response(data=data)
