from enterprise.models import PostRecruitment, User, EnterpriseUser
from social.models import Message
from utils.qos import upload_file
from utils.response import response
from utils.status_code import PARAMS_ERROR, PERMISSION_ERROR, MYSQL_ERROR
from utils.view_decorator import login_required, allowed_methods


@allowed_methods(['POST'])
@login_required
def send_resume(request):
    """
    投递简历
    用户投递简历
    """
    user = request.user
    user: User
    # 判断用户是否为企业管理员,企业管理员不允许投递简历
    if user.enterprise_user and user.enterprise_user.role == 0:
        return response(code=PERMISSION_ERROR, msg='企业管理员不允许投递简历')
    # 获取参数
    post_recruitment_id = request.POST.get('post_recruitment_id', None)
    if not post_recruitment_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post_recruitment = PostRecruitment.objects.filter(id=post_recruitment_id).first()
    if not post_recruitment:
        return response(code=PARAMS_ERROR, msg='招聘信息不存在')
    # 判断用户是否已经投递过
    if user in post_recruitment.candidates.all():
        return response(code=PARAMS_ERROR, msg='您已经投递过了')
    # 上传简历
    resume = request.FILES.get('resume', None)
    # 如果用户没有上传简历,检查个人信息里是否有简历
    if not resume:
        resume_key = user.resume_key
        # 如果还没有简历,则不允许投递
        if not resume_key:
            return response(code=PARAMS_ERROR, msg='请先上传简历')
    # 上传简历
    else:
        resume_key = str(user.id) + str(post_recruitment.id) + resume.name
        with open('Static/' + resume_key, 'wb') as f:
            for chunk in resume.chunks():
                f.write(chunk)
        if not upload_file(resume_key, 'Static/' + resume_key):
            return response(code=MYSQL_ERROR, msg='上传简历失败')
    # 记录应聘人员
    post_recruitment: PostRecruitment
    post_recruitment.candidates.add(user, through_defaults={'resume_key': resume_key})
    post_recruitment.save()
    return response(msg='投递成功')


@allowed_methods(['POST'])
@login_required
def accept_hire(request):
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
                                                    role=1, position=post_recruitment.post.name)
    enterprise_user.save()
    user.enterprise_user = enterprise_user
    user.save()
    return response(msg='接受录用成功')
