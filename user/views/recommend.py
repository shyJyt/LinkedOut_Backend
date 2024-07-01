import random

from enterprise.models import PostRecruitment
from enterprise.models import User

from utils.view_decorator import allowed_methods, login_required, guest_and_user
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS
from utils.qos import get_file

@allowed_methods(['GET'])
@guest_and_user
def get_recommend_recruit(request):
    """
    获取用户所有的意向岗位的招聘信息
    """
    all_recruit_info_list = []

    user = request.user

    if user:
        user: User
        interested_posts = user.interested_post.all()

    if user and len(interested_posts) > 0:
        # 用户已填写意向岗位
        for post in interested_posts:
            recruit_info_list = []
            recruit_info_res = PostRecruitment.objects.filter(post=post).all()

            # 如果没有招聘信息，跳过
            if len(recruit_info_res) == 0:
                continue

            for recruit_info in recruit_info_res:
                recruit_info_list.append({
                    'recruit_id': recruit_info.id,
                    'enterprise_id': recruit_info.enterprise.id,
                    'enterprise_name': recruit_info.enterprise.name,
                    'recruit_number': recruit_info.recruit_number,
                    'work_place': recruit_info.work_place,
                    'salary': recruit_info.salary,
                    'requirement': recruit_info.requirement,
                    'work_content': recruit_info.work_content,
                    'work_experience': recruit_info.work_experience,
                    'education': recruit_info.education
                })

            all_recruit_info_list.append({
                'post_name': post.name,
                'recruit_info_list': recruit_info_list  
            })
    else:
        # 游客 / 未填写意向岗位的用户
        # 获取所有的招聘信息
        recruit_info_res = PostRecruitment.objects.all()
        ids = []
        for recruit_info in recruit_info_res:
            ids.append(recruit_info.id)

        # 随机选取 5 个招聘信息
        target_num = min(5, len(ids))
        target_id = []
        while len(target_id) < target_num:
            tmp_id = random.choice(ids)
            if tmp_id not in target_id:
                target_id.append(tmp_id)

        for recruit_id in target_id:
            recruit_info = PostRecruitment.objects.get(id=recruit_id)
            all_recruit_info_list.append({
                'recruit_id': recruit_info.id,
                'enterprise_id': recruit_info.enterprise.id,
                'enterprise_name': recruit_info.enterprise.name,
                'enterprise_img_url': get_file(recruit_info.enterprise.img_url),
                'post_name': recruit_info.post.name,
                'recruit_number': recruit_info.recruit_number,
                'work_place': recruit_info.work_place,
                'salary': recruit_info.salary,
                'requirement': recruit_info.requirement,
                'work_content': recruit_info.work_content,
                'work_experience': recruit_info.work_experience,
                'education': recruit_info.education
            })

    return response(SUCCESS, '获取招聘信息成功！', data=all_recruit_info_list)


@allowed_methods(['GET'])
@login_required
def get_recommend_user(request):
    """
    获取相似用户，用户或者在职员工，分两个接口也行
    """
    user = request.user
    user: User
    interested_posts = user.interested_post.all()

    if len(interested_posts) == 0:
        return response(PARAMS_ERROR, '还未填写意向岗位！', error=True)

    all_job_seeker_list = []

    for post in interested_posts:
        job_seeker_list = post.interested_user.all()

        # 如果没有具有相同兴趣岗位的用户，跳过
        if len(job_seeker_list) == 0:
            continue

        all_job_seeker_list.append({
            'post_name': post.name,
            'job_seeker_list': [job_seeker.to_string() for job_seeker in job_seeker_list]
        })

    return response(SUCCESS, '获取相似用户成功！', data=all_job_seeker_list)
