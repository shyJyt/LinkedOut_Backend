from enterprise.models import PostRecruitment, User, EnterpriseUser
from social.models import Message
from utils.response import response
from utils.status_code import PARAMS_ERROR, PERMISSION_ERROR, MYSQL_ERROR
from utils.view_decorator import login_required, allowed_methods


@allowed_methods(['POST'])
@login_required
def sendResume(request):
    """
    投递简历
    用户投递简历
    """
    user = request.user
    user: User
    # 获取参数
    post_recruitment_id = request.POST.get('post_recruitment_id', None)
    if not post_recruitment_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post_recruitment = PostRecruitment.objects.filter(id=post_recruitment_id).first()
    if not post_recruitment:
        return response(code=PARAMS_ERROR, msg='招聘信息不存在')
    # 判断用户是否已经投递过
    if user in post_recruitment.user.all():
        return response(code=PARAMS_ERROR, msg='您已经投递过了')
    # 记录应聘人员
    post_recruitment: PostRecruitment
    post_recruitment.user.add(user)
    post_recruitment.save()
    return response(msg='投递成功')


@allowed_methods(['POST'])
@login_required
def acceptHire(request):
    """
    接受录用
    用户接受录用
    """
    user = request.user
    user: User
    # 获取参数
    post_recruitment_id = request.POST.get('post_recruitment_id', None)
    if not post_recruitment_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post_recruitment = PostRecruitment.objects.filter(id=post_recruitment_id).first()
    if not post_recruitment:
        return response(code=MYSQL_ERROR, msg='招聘信息不存在')
    # 判断用户是否已经属于某公司
    if user.enterprise_user:
        return response(code=PERMISSION_ERROR, msg='您已经属于某公司')
    # 判断用户是否已经被录用
    post_recruitment: PostRecruitment
    if user not in post_recruitment.accepted_user.all():
        return response(code=PERMISSION_ERROR, msg='您未被录用')
    # 为用户创建企业用户
    enterprise_user = EnterpriseUser.objects.create(enterprise=post_recruitment.enterprise,
                                                    user=user, role=1, position=post_recruitment.post.name)
    enterprise_user.save()
    user.enterprise_user = enterprise_user
    user.save()
    return response(msg='接受录用成功')
