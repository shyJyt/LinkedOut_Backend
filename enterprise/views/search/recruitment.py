from enterprise.models import Enterprise, PostRecruitment, Post
from utils.response import response
from utils.status_code import PARAMS_ERROR
from utils.view_decorator import allowed_methods


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
    return response(msg='获取企业招聘信息成功', data=data)


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


@allowed_methods(['GET'])
def searchPost(request):
    """
    筛选岗位,条件为以下之一:
    岗位名称，工作地点，薪资待遇（上限/下限/面议），
    学历要求，工作经验（上限/下限/无要求）要求
    企业id,与上述条件之一结合,可有可无
    """
    post_name = request.GET.get('post_name', None)
    work_place = request.GET.get('work_place', None)
    salary_range = request.GET.getlist('salary', None)
    education = request.GET.get('education', None)
    work_experience_range = request.GET.getlist('work_experience', None)
    enterprise_id = request.GET.get('enterprise_id', None)
    if not any([post_name, work_place, salary_range, education, work_experience_range, enterprise_id]):
        return response(code=PARAMS_ERROR, msg='参数不完整')
    post = None
    # 筛选企业,如果有企业id,先用企业id筛出一个queryset,再用queryset筛选岗位
    if enterprise_id:
        enterprise = Enterprise.objects.filter(id=enterprise_id).first()
        if not enterprise:
            return response(code=PARAMS_ERROR, msg='企业不存在')
        post = PostRecruitment.objects.filter(enterprise_id=enterprise)
    if post_name:
        post = post.filter(post__name__contains=post_name)
    if work_place:
        post = post.filter(work_place__contains=work_place)
    if salary_range:
        if salary_range[0] == '-1':
            salary = '面议'
        else:
            salary = str(salary_range[0]) + '-' + str(salary_range[1]) + '元'
        post = post.filter(salary=salary)
    if education:
        post = post.filter(education=education)
    if work_experience_range:
        if work_experience_range[0] == '-1':
            work_experience = '无要求'
        else:
            work_experience = str(work_experience_range[0]) + '-' + str(work_experience_range[1]) + '年'
        post = post.filter(work_experience=work_experience)
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
    return response(msg='获取岗位信息成功', data=data)
