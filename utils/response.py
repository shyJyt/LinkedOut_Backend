from django.http import JsonResponse
from .status_code import *


def response(code=SUCCESS, msg='', data=None, error=False):
    return JsonResponse({
        'code': code,
        'msg': msg,
        'data': data,
        'error': error
    })
