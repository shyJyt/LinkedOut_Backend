from enterprise.models import PostRecruitment
from user.models import User
from utils.response import response
from utils.status_code import *
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
    # 不能是企业用户
    if user.enterprise_user is not None:
        return response(code=PERMISSION, msg='您是企业用户,不能投递简历')
    # 获取参数
    post_recruitment_id = request.POST.get('post_recruitment_id', None)
    if not post_recruitment_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post_recruitment = PostRecruitment.objects.filter(id=post_recruitment_id).first()
    if not post_recruitment:
        return response(code=PARAMS_ERROR, msg='招聘信息不存在')
    # 记录应聘人员
    post_recruitment: PostRecruitment
    post_recruitment.user.add(user)
    post_recruitment.save()
    return response(msg='投递成功')