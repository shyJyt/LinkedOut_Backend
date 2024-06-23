import re
import os

from utils.qos import *
from utils.token import *
from utils.md5 import *
from utils.view_decorator import *
from utils.email import *
from utils.generate_avatar import render_identicon

from user.models import User


def login(request):
    """
    登录
    :param request: email, password
    :return: [code, msg, data], 其中data为token(若登录成功,否则为None)
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        email = request.POST.get('email', None)
        password = request.POST.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
                salt = user.salt
                password_encode = create_md5(password, salt)
                if password_encode != user.password:
                    return response(PARAMS_ERROR, '邮箱或密码错误！', error=True)
                else:
                    user_info = {'email': user.email, 'nickname': user.nickname}
                    token = generate_token(user_info, 60 * 60 * 24)
                    data = {
                        'token': token,
                        'nickname': user.nickname,
                        'avatar': get_file(user.avatar_key)
                    }
                    return response(SUCCESS, '登录成功！', data=data)
            except User.DoesNotExist:
                return response(MYSQL_ERROR, '用户不存在！', error=True)
        else:
            return response(PARAMS_ERROR, '邮箱和密码不可为空', error=True)


def register_view(request):
    """
    注册
    :param request: email, name, password, password_repeat
    :return: [code, msg, data] 其中data中有验证码
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        nickname = request.POST.get('nickname', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        password_repeat = request.POST.get('password_repeat', None)
        if nickname and password and password_repeat and email:
            re_str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
            if not re.match(re_str, email):
                return response(PARAMS_ERROR, '邮箱格式错误！', error=True)
            if User.objects.filter(email=email):
                return response(PARAMS_ERROR, '邮箱已注册过！', error=True)
            if password != password_repeat:
                return response(PARAMS_ERROR, '两次密码不一致！', error=True)
            # 发送邮件
            try:
                code = send_email(email)
            except Exception:
                return response(PARAMS_ERROR, '发送邮件失败！', error=True)

            # 生成盐并加密密码
            salt = create_salt()
            password_encode = create_md5(password, salt)

            # 创建用户, is_active=False, 未激活, 激活后才能登录,update_or_create,如果存在则更新,不存在则创建
            default_fields = {'nickname': nickname, 'password': password_encode, 'salt': salt}
            User.objects.update_or_create(defaults=default_fields, email=email)

            return response(SUCCESS, '请注意查收邮件！', data=code)
        else:
            return response(PARAMS_ERROR, '提交字段名不可为空！', error=True)


def active_user(request):
    """
    激活用户
    :param request: correct_code(验证码), get_code(用户输入验证码), email
    :return: [code, msg, data]
    """
    if request.method != "POST":
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        correct_code = request.POST.get('correct_code', None)
        get_code = request.POST.get('get_code', None)
        email = request.POST.get('email', None)
        if email and get_code and correct_code:
            try:
                user = User.objects.get(email=email, is_active=False)
                if get_code == correct_code:
                    # 激活用户并保存
                    user.is_active = True
                    user.save()
                    # 注册成功后给用户生成默认头像
                    init_user_avatar(user)
                    # 注册成功后直接登录,返回 token
                    user_info = {
                        'email': user.email,
                        'nickname': user.nickname
                    }
                    token = generate_token(user_info, 60 * 60 * 24)
                    # 返回头像 url
                    data = {
                        'token': token,
                        'nickname': user.nickname,
                        'avatar': get_file(user.avatar_key)
                    }
                    return response(SUCCESS, '注册成功', data=data)
                else:
                    return response(PARAMS_ERROR, '验证码错误', error=True)
            except User.DoesNotExist:
                return response(MYSQL_ERROR, '该用户已经注册过', error=True)
        else:
            return response(PARAMS_ERROR, '提交字段名不可为空！', error=True)


def init_user_avatar(user: User) -> str:
    """
    初始化用户头像
    :param user: 用户对象
    """
    email = user.email
    key = email + '_avatar.png'
    # 生成头像并上传
    render_identicon(key)
    upload_file(key, 'tempFile/' + key)
    user.avatar_key = key
    user.save()
    # 删除本地存储的文件
    path_file = 'tempFile/' + key
    os.remove(path_file)

    return key


@allowed_methods(['GET'])
@login_required
def get_user_info(request):
    """
    获取用户信息
    :param request: token
    :return: [code, msg, data, error], 其中data为用户信息
    """
    user = request.user
    user: User
    data = user.to_string()
    return response(SUCCESS, '获取用户信息成功！', data=data)


@allowed_methods(['POST'])
@login_required
def update_user_info(request):
    """
    更新用户信息
    """
    if request.method != 'POST':
        return response(METHOD_ERROR, '请求方法错误', error=True)
    else:
        user = request.user
        user: User

        nickname = request.POST.get('nickname', None)
        real_name = request.POST.get('real_name', None)
        education = request.POST.get('education', None)
        work_city = request.POST.get('work_city', None)
        blog_link = request.POST.get('blog_link', None)
        github_link = request.POST.get('github_link', None)
        if nickname:
            user.nickname = nickname
        if real_name:
            user.real_name = real_name
        if education:
            user.education = education
        if work_city:
            user.work_city = work_city
        if blog_link:
            user.blog_link = blog_link
        if github_link:
            user.github_link = github_link

        user.save()
        return response(SUCCESS, '更新用户信息成功！')
