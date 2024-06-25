from enterprise.models import EnterpriseUser, User
from social.models import Message
from utils.response import response
from utils.status_code import *
from utils.view_decorator import login_required, allowed_methods


@allowed_methods(['POST'])
@login_required
def addEmployee(request):
    """
    添加员工
    企业管理员添加员工
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION, msg='您不是企业管理员')
    # 获取参数
    user_id = request.POST.get('user_id', None)
    if not user_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找用户
    employee = User.objects.filter(id=user_id).first()
    if not employee:
        return response(code=PARAMS_ERROR, msg='用户不存在')
    # 发送消息
    message_params = {
        'from_user_id': user_id,
        'to_user_id': employee.id,
        'type': 0,
        'title': '邀请加入企业',
        'content': '管理员邀请你加入企业' + str(user.enterprise_user.enterprise.name),
    }
    Message.objects.create(**message_params)
    return response(msg='邀请成功')


@allowed_methods(['POST'])
@login_required
def expelEmployee(request):
    """
    开除员工
    企业管理员开除员工
    """
    user = request.user
    user: User
    # 查看用户是否为企业管理员
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION, msg='您不是企业管理员')
    # 获取参数
    employee_id = request.POST.get('employee_id', None)
    if not employee_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查找用户
    employee = EnterpriseUser.objects.filter(id=employee_id).first()
    if not employee:
        return response(code=PARAMS_ERROR, msg='员工不存在')
    # 发送消息
    message_params = {
        'from_user_id': user.id,
        'to_user_id': employee.user_id,
        'type': 0,
        'title': '开除通知',
        'content': '管理员开除了你',
    }
    Message.objects.create(**message_params)
    # 删除企业用户
    employee_user = employee.user
    employee.delete()
    employee_user.enterprise_user = None
    employee_user.save()
    return response(msg='开除成功')
