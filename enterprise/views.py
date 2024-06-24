from django.shortcuts import render
from utils.response import response
from utils.view_decorator import login_required, allowed_methods
from utils.status_code import *
from utils.qos import *
from .models import *
from user.models import User


# Create your views here.
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
    from_user_id = user.id
    to_user_id = user_id
    enterprise = user.enterprise_user.enterprise
    content = '管理员邀请你加入企业' + str(enterprise.id)
    # TODO 发送消息
    pass
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
    # TODO 发送消息
    from_user_id = user.id
    to_user_id = employee_id
    enterprise = user.enterprise_user.enterprise
    content = '管理员开除了你'
    pass
    # 删除企业用户
    employee_user = employee.user
    employee.delete()
    employee_user.enterprise_user = None
    employee_user.save()
    return response(msg='开除成功')


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
    用户完善企业信息,如工龄、岗位等
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
def updateEnterpriseInfo(request):
    """
    企业管理员可修改企业信息,如名称、简介、图片等
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION, msg='您不是企业管理员')
    # 获取参数
    intro = request.POST.get('intro', None)
    img = request.FILES.get('img', None)
    # 查找企业
    enterprise = user.enterprise_user.enterprise
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    # 更新字段
    if intro:
        enterprise.intro = intro
    if img:
        img_url = 'enterprise/' + img.name
        with open('static/' + img_url, 'wb') as f:
            for chunk in img.chunks():
                f.write(chunk)
        if not upload_file(img_url, 'static/' + img_url):
            return response(code=SERVER_ERROR, msg='上传图片失败')
        enterprise.img_url = img_url
    enterprise.save()
    return response(msg='修改成功')


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


@allowed_methods(['GET'])
def searchEnterprise(request):
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
        data.append({
            'id': e.id,
            'name': e.name,
            'intro': e.intro,
            'img_url': e.img_url
        })
    return response(data=data)


@allowed_methods(['GET'])
def getEnterpriseInfo(request):
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
    data = {
        'name': enterprise.name,
        'intro': enterprise.intro,
        'img_url': enterprise.img_url
    }
    return response(data=data)


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
def getRecruitment(request):
    """
    获取招聘信息
    用户查看某个企业招聘信息
    返回岗位列表
    """
    enterprise_id = request.GET.get('enterprise_id', None)
    if not enterprise_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    enterprise = Enterprise.objects.filter(id=enterprise_id).first()
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    post_recruitment = PostRecruitment.objects.filter(enterprise_id=enterprise)
    data = []
    for e in post_recruitment:
        data.append({
            'post_recruitment_id': e.id,
            'post_name': e.post.name
        })
    return response(msg='获取企业找平信息成功', data=data)


@allowed_methods(['GET'])
def getPostRecruitment(request):
    """
    获取岗位招聘信息
    用户查看某个企业某个岗位的招聘信息
    """
    post_recruitment_id = request.GET.get('post_recruitment_id', None)
    if not post_recruitment_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post_recruitment = PostRecruitment.objects.filter(id=post_recruitment_id).first()
    if not post_recruitment:
        return response(code=PARAMS_ERROR, msg='招聘信息不存在')
    data = {
        'post_name': post_recruitment.post.name,
        'recruit_number': post_recruitment.recruit_number,
        'work_place': post_recruitment.work_place,
        'salary': post_recruitment.salary,
        'education': post_recruitment.education,
        'work_experience': post_recruitment.work_experience,
        'work_content': post_recruitment.work_content,
        'requirement': post_recruitment.requirement
    }
    return response(msg='获取招聘信息成功', data=data)


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
    return response(data=user.resume_url)


@allowed_methods(['GET'])
def searchPost(request):
    """
    筛选岗位,条件为以下之一:
    岗位名称，工作地点，薪资待遇（上限/下限/面议），
    学历要求，工作经验（上限/下限/无要求）要求
    """
    user = request.user
    user: User
    post_name = request.GET.get('post_name', None)
    work_place = request.GET.get('work_place', None)
    salary_range = request.GET.getlist('salary', None)
    education = request.GET.get('education', None)
    work_experience_range = request.GET.getlist('work_experience', None)
    if not any([post_name, work_place, salary_range, education, work_experience_range]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post = None
    if post_name:
        post = Post.objects.filter(name__contains=post_name)
    if work_place:
        post = PostRecruitment.objects.filter(work_place=work_place)
    if salary_range:
        if salary_range[0] == '-1':
            salary = '面议'
        else:
            salary = str(salary_range[0]) + '-' + str(salary_range[1]) + '元'
        post = PostRecruitment.objects.filter(salary=salary)
    if education:
        post = PostRecruitment.objects.filter(education=education)
    if work_experience_range:
        if work_experience_range[0] == '-1':
            work_experience = '无要求'
        else:
            work_experience = str(work_experience_range[0]) + '-' + str(work_experience_range[1]) + '年'
        post = PostRecruitment.objects.filter(work_experience=work_experience)
    if not post:
        return response(code=PARAMS_ERROR, msg='没有符合条件的岗位')
    data = []
    for p in post:
        data.append({
            'post_recruitment_id': p.id,
            'post_name': p.post.name,
            'work_place': p.work_place,
            'salary': p.salary,
            'education': p.education,
            'work_experience': p.work_experience,
        })
