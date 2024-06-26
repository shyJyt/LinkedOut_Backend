from enterprise.models import EnterpriseUser, User, Invitation
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
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
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
        'from_user_id': user,
        'to_user_id': employee,
        'type': 0,
        'title': '邀请加入企业',
        'content': '管理员邀请你加入企业' + str(user.enterprise_user.enterprise.name),
        'obj_id': user.enterprise_user.enterprise.id,
    }
    message = Message.objects.create(**message_params)
    message.save()
    # 创建邀请
    invitation_params = {
        'from_user': user,
        'to_user': employee,
        'obj_id': user.enterprise_user.enterprise.id,
    }
    invitation = Invitation.objects.create(**invitation_params)
    invitation.save()
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
        'from_user_id': user,
        'to_user_id': employee_user,
        'type': 0,
        'title': '开除通知',
        'content': '管理员开除了你',
    }
    message = Message.objects.create(**message_params)
    message.save()
    print(message)
    return response(msg='开除成功')
