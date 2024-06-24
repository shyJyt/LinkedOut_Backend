from utils.qos import *
from utils.token import *
from utils.md5 import *
from utils.view_decorator import *
from utils.email import *

@allowed_methods(['GET'])
def search_user(request):
    """
    通过名字模糊搜索用户（未分页）
    """
    keyword = request.GET.get('keyword', None)
    if keyword:
        users = User.objects.filter(nickname__contains=keyword)
        user_list = []
        for user in users:
            user_list.append(user.to_string())
        return response(SUCCESS, '搜索用户成功！', data=user_list)
    else:
        return response(PARAMS_ERROR, '关键字不可为空！', error=True)
