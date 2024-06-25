import os

from user.models import User

from utils.qos import upload_file, save_file_local, get_file
from utils.view_decorator import allowed_methods, login_required
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS, MYSQL_ERROR, OSS_ERROR

@allowed_methods(['POST'])
@login_required
def update_user_info(request):
    """
    更新用户信息，不包括头像和简历
    """
    user = request.user
    user: User

    nickname = request.POST.get('nickname', None)
    real_name = request.POST.get('real_name', None)
    education = request.POST.get('education', None)
    interested_posts = request.POST.getlist('interested_posts', None)
    work_city = request.POST.get('work_city', None)
    blog_link = request.POST.get('blog_link', None)
    github_link = request.POST.get('github_link', None)
    if nickname:
        user.nickname = nickname
    if real_name:
        user.real_name = real_name
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

    user.save()
    return response(SUCCESS, '更新用户信息成功！')


@allowed_methods(['POST'])
@login_required
def upload_user_avatar(request):
    """
    上传用户头像
    """
    user = request.user
    user: User
    avatar = request.FILES.get('avatar', None)

    if avatar:
        local_file = save_file_local(avatar)
        key = str(user.id) + '_avatar.png'
        # 上传到七牛云
        ret = upload_file(key, local_file)
        os.remove(local_file)
        if ret:
            user.avatar_key = key
        else:
            return response(OSS_ERROR, '上传头像失败！', error=True)
        user.save()
        return response(SUCCESS, '上传头像成功！')
    else:
        return response(PARAMS_ERROR, '未上传头像！', error=True)


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
        key = str(user.id) + '_resume.pdf'
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
    user_info = user.to_string()
    return response(SUCCESS, '获取用户信息成功！', data=user_info)


@allowed_methods(['GET'])
def get_certain_user_info(request):
    """
    获取指定用户信息
    """
    user_id = request.GET.get('user_id', None)
    if user_id:
        try:
            user = User.objects.get(id=user_id, is_active=True)
            user_info = user.to_string()
            # TODO: 不加 login_required 装饰器如何获得登录用户和目标用户的关系？

            return response(SUCCESS, '获取用户信息成功！', data=user_info)
        except User.DoesNotExist:
            return response(MYSQL_ERROR, '用户不存在！', error=True)
    else:
        return response(PARAMS_ERROR, '用户id不可为空！', error=True)


@allowed_methods(['GET'])
@login_required
def user_download_resume(request):
    """
    下载用户简历
    """
    user = request.user
    user: User
    resume_key = user.resume_key
    if resume_key:
        data = {
            'resume_url': get_file(resume_key)
        }
        return response(SUCCESS, '获取简历下载链接成功！', data=data)
    else:
        return response(PARAMS_ERROR, '用户未上传简历！', error=True)
    