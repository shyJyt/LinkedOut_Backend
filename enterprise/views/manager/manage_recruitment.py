from enterprise.models import Post, PostRecruitment, User
from social.models import Message
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, login_required
from utils.qos import get_file


@allowed_methods(['POST'])
@login_required
def post_recruitment(request):
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
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
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
    # 薪资和经验处理 形式 ['0, 100'],先转为[‘0’，‘100’]
    salary_range = [i for i in salary_range[0].split(',')]
    if salary_range[0] == '-1':
        salary = '面议'
    else:
        salary = str(salary_range[0]) + '-' + str(salary_range[1]) + 'k'
    work_experience_range = [i for i in work_experience_range[0].split(',')]
    if work_experience_range[0] == '-1':
        work_experience = '无要求'
    else:
        work_experience = str(work_experience_range[0]) + '-' + str(work_experience_range[1]) + '年'
    # 创建招聘信息
    post_recruitment = PostRecruitment.objects.create(enterprise=user.enterprise_user.enterprise, post=post,
                                                      recruit_number=recruit_number, work_content=work_content,
                                                      work_place=work_place, salary=salary, education=education,
                                                      work_experience=work_experience,
                                                      requirement=job_requirements)
    post_recruitment.save()
    data = {
        'post_id': post_recruitment.id
    }
    return response(msg='发布成功', data=data)


@allowed_methods(['GET'])
@login_required
def get_candidates(request):
    """
    获取相应岗位下的相应人员列表
    返回用户id和real_name
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    post_recruitment_id = request.GET.get('post_recruitment_id', None)
    if not post_recruitment_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post_recruitment = PostRecruitment.objects.filter(id=post_recruitment_id).first()
    if not post_recruitment:
        return response(code=PARAMS_ERROR, msg='招聘信息不存在')
    data = []
    post_recruitment: PostRecruitment
    for u in post_recruitment.user.all():
        # 获取应聘人员简历,头像
        resume_url = get_file(u.resume_key)
        avatar_url = get_file(u.avatar_key)
        data.append({
            'user_id': u.id,
            'real_name': u.real_name,
            'resume_url': resume_url,
            'avatar_url': avatar_url
        })
    return response(data=data)


@allowed_methods(['GET'])
@login_required
def get_resume(request):
    """
    获取某个应聘者的简历
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    user_id = request.GET.get('user_id', None)
    if not user_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    user = User.objects.filter(id=user_id).first()
    if not user:
        return response(code=PARAMS_ERROR, msg='用户不存在')
    # 返回简历url
    if user.resume_key is None:
        return response(code=PARAMS_ERROR, msg='用户未上传简历')
    resume_url = get_file(user.resume_key)
    print('here' + resume_url)
    if resume_url == '':
        return response(code=SERVER_ERROR, msg='获取简历失败')
    data = {
        'resume_url': resume_url
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
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    candidate_id = request.POST.get('candidate_id', None)
    post_id = request.POST.get('post_id', None)
    if not all([candidate_id, post_id]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    # 查看招聘信息是否存在
    post_recruitment = PostRecruitment.objects.filter(id=post_id).first()
    if not post_recruitment:
        return response(code=PARAMS_ERROR, msg='招聘信息不存在')
    candidate = post_recruitment.user.filter(id=candidate_id).first()
    if not candidate:
        return response(code=PARAMS_ERROR, msg='候选人不存在')
    # 是否是自己,即企业管理员
    if candidate == user:
        return response(code=PERMISSION_ERROR, msg='您不能录用自己')
    # 是否已经被录用
    if candidate in post_recruitment.accepted_user.all():
        return response(code=MYSQL_ERROR, msg='该用户已被录用')
    # 发送消息
    message_params = {
        'from_user_id': user,
        'to_user_id': candidate,
        'type': 0,
        'title': '录用信息',
        'content': '恭喜你被公司' + str(user.enterprise_user.enterprise.name) + '录用',
        'obj_id': post_recruitment.id,
    }
    Message.objects.create(**message_params)
    # 对应岗位招聘信息中的招聘人数减一
    number = int(post_recruitment.recruit_number)
    number -= 1
    post_recruitment.recruit_number = str(number)
    post_recruitment.save()
    # 将候选人添加到已录用人员中
    post_recruitment.accepted_user.add(candidate)
    post_recruitment.save()
    # 将剩余的招聘人数返回
    return response(msg='发送成功', data={'recruit_number': post_recruitment.recruit_number})
