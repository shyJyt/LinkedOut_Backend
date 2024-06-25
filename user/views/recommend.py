from enterprise.models import PostRecruitment
from enterprise.models import User

from utils.view_decorator import allowed_methods, login_required
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS

@allowed_methods(['GET'])
@login_required
def get_recruit_info(request):
    """
    获取用户所有的意向岗位的招聘信息
    """
    user = request.user
    user: User
    interested_posts = user.interested_post.all()

    if len(interested_posts) == 0:
        return response(PARAMS_ERROR, '还未填写意向岗位！', error=True)

    all_recruit_info_list = []
    for post in interested_posts:
        recruit_info_list = PostRecruitment.objects.filter(post=post).all()
        all_recruit_info_list.append({
            'post_name': post.name,
            'recruit_info_list': [recruit_info.to_string() for recruit_info in recruit_info_list]
        })

    return response(SUCCESS, '获取招聘信息成功！', data=all_recruit_info_list)


@allowed_methods(['GET'])
@login_required
def get_similar_enterprise(request):
    """
    获取相似企业，感觉招聘信息涵盖了
    """
    pass


@allowed_methods(['GET'])
@login_required
def get_similar_user(request):
    """
    获取相似用户，求职者或者在职员工，分两个接口也行
    """
    user = request.user
    user: User
    interested_posts = user.interested_post.all()

    if len(interested_posts) == 0:
        return response(PARAMS_ERROR, '还未填写意向岗位！', error=True)

    all_job_seeker_list = []

    for post in interested_posts:
        job_seeker_list = post.interested_user.all()
        all_job_seeker_list.append({
            'post_name': post.name,
            'job_seeker_list': [job_seeker.to_string() for job_seeker in job_seeker_list]
        })

    return response(SUCCESS, '获取相似用户成功！', data=all_job_seeker_list)
