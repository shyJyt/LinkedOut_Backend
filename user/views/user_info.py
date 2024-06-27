import os

from enterprise.models import User, EnterpriseUser

from utils.qos import upload_file, save_file_local, generate_time_stamp
from utils.view_decorator import allowed_methods, login_required, guest_and_user
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS, MYSQL_ERROR, OSS_ERROR

@allowed_methods(['POST'])
@login_required
def update_user_info(request):
    """
    更新用户信息，不包括简历
    """
    user = request.user
    user: User

    nickname = request.POST.get('nickname', None)
    real_name = request.POST.get('real_name', None)
    age = request.POST.get('age', None)
    education = request.POST.get('education', None)
    interested_posts = request.POST.getlist('interested_posts', None)
    work_city = request.POST.get('work_city', None)
    blog_link = request.POST.get('blog_link', None)
    github_link = request.POST.get('github_link', None)
    avatar = request.FILES.get('avatar', None)

    if nickname:
        user.nickname = nickname
    if real_name:
        user.real_name = real_name
    if age:
        user.age = age
    if education:
        user.education = education
    if interested_posts:
        user.interested_post.clear()
        for post_id in interested_posts:
            user.interested_post.add(post_id)
    if work_city:
        user.work_city = work_city
    if blog_link:
        user.blog_link = blog_link
    if github_link:
        user.github_link = github_link
    if avatar:
        local_file = save_file_local(avatar)
        key = str(user.id) + '_avatar_'+ generate_time_stamp() + '.png'
        # 上传到七牛云
        ret = upload_file(key, local_file)
        os.remove(local_file)
        if ret:
            user.avatar_key = key
        else:
            return response(OSS_ERROR, '上传头像失败！', error=True)

    user.save()
    return response(SUCCESS, '更新用户信息成功！')


@allowed_methods(['POST'])
@login_required
def upload_resume(request):
    """
    上传简历
    """
    user = request.user
    user: User
    resume = request.FILES.get('resume', None)

    if resume:
        local_file = save_file_local(resume)
        key = str(user.id) + '_resume_'+ generate_time_stamp() + '.pdf'
        # 上传到七牛云
        ret = upload_file(key, local_file)
        os.remove(local_file)
        if ret:
            user.resume_key = key
        else:
            return response(OSS_ERROR, '上传简历失败！', error=True)
        user.save()
        return response(SUCCESS, '上传简历成功！')
    else:
        return response(PARAMS_ERROR, '未上传简历！', error=True)


@allowed_methods(['GET'])
@login_required
def get_user_info(request):
    """
    获取登录用户的信息
    :param request: token
    :return: [code, msg, data, error], 其中data为用户信息
    """
    user = request.user
    user: User
    user_info = user.get_all_user_info()

    return response(SUCCESS, '获取用户信息成功！', data=user_info)


@allowed_methods(['GET'])
@guest_and_user
def get_user_info_by_id(request):
    """
    获取指定用户信息
    """
    user_id = request.GET.get('user_id', None)
    if user_id:
        try:
            target_user = User.objects.get(id=user_id, is_active=True)
            user_info = target_user.get_all_user_info()
            
            if request.user:
                # 用户查看指定用户，还要返回是否关注
                user = request.user
                user: User
                if user.follow_user.filter(id=user_id).exists():
                    user_info['is_follow'] = True
                else:
                    user_info['is_follow'] = False
            else:
                # 游客查看指定用户
                user_info['is_follow'] = False

            return response(SUCCESS, '获取用户信息成功！', data=user_info)
        except User.DoesNotExist:
            return response(MYSQL_ERROR, '用户不存在！', error=True)
    else:
        return response(PARAMS_ERROR, '用户id不可为空！', error=True)
    