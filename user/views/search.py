from enterprise.models import User

from utils.view_decorator import allowed_methods, guest_and_user
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS

@allowed_methods(['GET'])
@guest_and_user
def search_user(request):
    """
    通过模糊搜索用户（未分页）
    """
    keyword = request.GET.get('keyword', None)
    if keyword:
        res_users = User.objects.filter(nickname__contains=keyword)
        user_list = []

        user = request.user
        user: User

        if user:
            for res_user in res_users:
                user_info = res_user.get_all_user_info()    
                user_info['is_follow'] = user.follow_user.filter(id=res_user.id).exists()
                user_list.append(user_info)
        else:
            for res_user in res_users:
                user_info = res_user.get_all_user_info()    
                user_info['is_follow'] = False
                user_list.append(user_info)

        return response(SUCCESS, '搜索用户成功！', data=user_list)
    else:
        return response(PARAMS_ERROR, '关键字不可为空！', error=True)
