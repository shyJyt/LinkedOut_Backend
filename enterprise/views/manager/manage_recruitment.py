from enterprise.models import Post, PostRecruitment, User
from social.models import Message
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, login_required


@allowed_methods(['POST'])
@login_required
def postRecruitment(request):
    """
    发布招聘
    企业管理员发布招聘岗位要求和数量:
    岗位名称，工作地点，薪资待遇（上限/下限/面议），
    学历要求，工作经验（上限/下限/无要求），
    工作内容描述，任职要求，招聘人数
    其中薪资和经验用数组传入,都为-1表示无要求
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION, msg='您不是企业管理员')
    # 获取参数
    post_name = request.POST.get('post_name', None)
    work_place = request.POST.get('work_place', None)
    salary_range = request.POST.getlist('salary', None)
    education = request.POST.get('education', None)
    work_experience_range = request.POST.getlist('work_experience', None)
    work_content = request.POST.get('work_content', None)
    job_requirements = request.POST.get('job_requirements', None)
    recruit_number = request.POST.get('recruit_number', None)
    if not all([post_name, work_place, salary_range, education, work_experience_range, work_content, job_requirements,
                recruit_number]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 如果没有相应岗位则创建
    post = Post.objects.filter(name=post_name).first()
    if not post:
        post = Post.objects.create(name=post_name)
        post.save()
    # 薪资和经验处理
    if salary_range[0] == '-1':
        salary = '面议'
    else:
        salary = str(salary_range[0]) + '-' + str(salary_range[1]) + '元'
    if work_experience_range[0] == '-1':
        work_experience = '无要求'
    else:
        work_experience = str(work_experience_range[0]) + '-' + str(work_experience_range[1]) + '年'
    # 创建招聘信息
    post_recruitment = PostRecruitment.objects.create(enterprise_id=user.enterprise_user.enterprise, post_id=post,
                                                      recruit_number=recruit_number, work_content=work_content,
                                                      work_place=work_place, salary=salary, education=education,
                                                      work_experience=work_experience,
                                                      requirement=job_requirements)
    post_recruitment.save()
    return response(msg='发布成功')


@allowed_methods(['GET'])
@login_required
def getCandidates(request):
    """
    获取相应岗位下的相应人员列表
    返回用户id和real_name
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION, msg='您不是企业管理员')
    post_recruitment_id = request.GET.get('post_recruitment_id', None)
    if not post_recruitment_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post_recruitment = PostRecruitment.objects.filter(id=post_recruitment_id).first()
    if not post_recruitment:
        return response(code=PARAMS_ERROR, msg='招聘信息不存在')
    data = []
    post_recruitment: PostRecruitment
    for u in post_recruitment.user.all():
        data.append({
            'user_id': u.id,
            'real_name': u.real_name,
        })
    return response(data=data)


@allowed_methods(['GET'])
@login_required
def getResume(request):
    """
    获取某个应聘者的简历
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION, msg='您不是企业管理员')
    user_id = request.GET.get('user_id', None)
    if not user_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    user = User.objects.filter(id=user_id).first()
    if not user:
        return response(code=PARAMS_ERROR, msg='用户不存在')
    data = {
        'resume_url': user.resume_url
    }
    return response(data=data)


@allowed_methods(['POST'])
@login_required
def hire(request):
    """
    发送录取通知
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION, msg='您不是企业管理员')
    candidate_id = request.POST.get('candidate_id', None)
    if not candidate_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    user = User.objects.filter(id=candidate_id).first()
    if not user:
        return response(code=PARAMS_ERROR, msg='用户不存在')
    # 发送消息
    message_params = {
        'from_user_id': user.id,
        'to_user_id': candidate_id,
        'type': 0,
        'title': '录用信息',
        'content': '恭喜你被公司' + str(user.enterprise_user.enterprise.name) + '录用'
    }
    Message.objects.create(**message_params)
    return response(msg='发送成功')
