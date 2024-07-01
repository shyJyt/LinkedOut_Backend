from functools import wraps
from django.http import JsonResponse
from .status_code import *
from enterprise.models import User
from utils.response import response
from utils.token import get_value


def allowed_methods(methods):
    """
    装饰器，用于限制视图函数只能接受指定的HTTP请求方法。

    参数:
    - methods: 一个包含允许的HTTP请求方法的列表，如 ['GET', 'POST']。
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse({
                    'code': METHOD_ERROR,
                    'error': True,
                    'message': 'allowed method(s) are [{}]'.format(', '.join(methods)),
                    'data': {},
                })
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def login_required(view_func):
    """
    装饰器，用于限制视图函数只能在登录状态下访问。
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 取出token,查找是否有此用户,token放在HTTP请求的header中
        token = request.META.get('HTTP_TOKEN', None)
        if token:
            value = get_value(token)
            if value:
                # 找是否有user
                email = value.get('email', None)
                try:
                    user = User.objects.get(email=email, is_active=True)
                    request.user = user
                    return view_func(request, *args, **kwargs)
                except User.DoesNotExist:
                    return response(PARAMS_ERROR, '用户不存在', error=True)
            else:
                return response(PARAMS_ERROR, '用户未登录', error=True)
        else:
            return response(PARAMS_ERROR, '用户未登录', error=True)

    return _wrapped_view


def guest_and_user(view_func):
    """
    装饰器，视图函数可以在登录状态或游客状态下访问。
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 取出token,查找是否有此用户,token放在HTTP请求的header中
        token = request.META.get('HTTP_TOKEN', None)
        if token:
            value = get_value(token)
            if value:
                # 找是否有user
                email = value.get('email', None)
                try:
                    user = User.objects.get(email=email, is_active=True)
                    request.user = user
                    return view_func(request, *args, **kwargs)
                except User.DoesNotExist:
                    return response(PARAMS_ERROR, '用户不存在', error=True)
            else:
                return response(PARAMS_ERROR, '用户未登录', error=True)
        else:
            request.user = None
            return view_func(request, *args, **kwargs)

    return _wrapped_view


def get_user_from_token(token):
    if token:
        value = get_value(token)
        if value:
            email = value.get('email', None)
            try:
                user = User.objects.get(email=email, is_active=True)
                return user
            except User.DoesNotExist:
                return None
    return None
