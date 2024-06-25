import re
import os

from enterprise.models import User

from utils.qos import upload_file, get_file
from utils.token import generate_token
from utils.md5 import create_salt, create_md5
from utils.view_decorator import allowed_methods, login_required
from utils.email import send_email
from utils.generate_avatar import render_identicon
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS, MYSQL_ERROR

@allowed_methods(['POST'])
def login(request):
    """
    登录
    :param request: email, password
    :return: [code, msg, data], 其中data为token(若登录成功,否则为None)
    """
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


@allowed_methods(['POST'])
def register(request):
    """
    注册
    :param request: email, name, password, password_repeat
    :return: [code, msg, data] 其中data中有验证码
    """
    nickname = request.POST.get('nickname', None)
    real_name = request.POST.get('real_name', None)
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    password_repeat = request.POST.get('password_repeat', None)
    if nickname and real_name and password and password_repeat and email:
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
        default_fields = {'email': email, 'nickname': nickname, 'real_name': real_name, 'password': password_encode, 'salt': salt}
        User.objects.create(**default_fields)

        return response(SUCCESS, '请注意查收邮件！', data=code)
    else:
        return response(PARAMS_ERROR, '提交字段名不可为空！', error=True)


@allowed_methods(['POST'])
def active_user(request):
    """
    激活用户
    :param request: correct_code(验证码), get_code(用户输入验证码), email
    :return: [code, msg, data]
    """
    correct_code = request.POST.get('correct_code', None)
    get_code = request.POST.get('get_code', None)
    email = request.POST.get('email', None)

    if email and get_code and correct_code:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return response(MYSQL_ERROR, '待激活用户不存在', error=True)
        
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
    key = str(user.id) + '_avatar.png'

    # 先存到数据库
    user.avatar_key = key
    user.save()
    # 生成头像并上传
    render_identicon(key)
    upload_file(key, 'tempFile/' + key)
    # 删除本地存储的文件
    path_file = 'tempFile/' + key
    os.remove(path_file)

    return key


@allowed_methods(['GET'])
@login_required
def unsubscribe(request):
    """
    注销用户
    """
    # TODO 注销用户
    # 1、真注销：要删掉相关联的什么东西？会触发 on_delete
    # 全部级联删除是最稳妥的，但是会损失一些合理性，比如删除一个动态后，转发它的动态会被直接删除而不是显示原内容已被删除
    # 如果保留一部分表不被级联删除，要么置空，要么不用外键，查找的时候，需要判断存不存在来避免异常
    # 2、伪注销：把 is_active 置为 False，不会触发 on_delete
    # 同样需要判断用户是否已注销，但是最坏也就是已注销用户的信息被获取，不会出现异常

    pass
