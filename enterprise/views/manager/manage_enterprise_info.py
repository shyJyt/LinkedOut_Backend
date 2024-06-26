from enterprise.models import User
from utils.qos import upload_file
from utils.response import response
from utils.status_code import PERMISSION_ERROR, PARAMS_ERROR, SERVER_ERROR
from utils.view_decorator import login_required, allowed_methods


@allowed_methods(['POST'])
@login_required
def updateEnterpriseInfo(request):
    """
    企业管理员可修改企业信息,如名称、简介、图片等
    """
    user = request.user
    user: User
    # 查看用户是否为企业用户
    if user.enterprise_user is None or user.enterprise_user.role != 0:
        return response(code=PERMISSION_ERROR, msg='您不是企业管理员')
    # 获取参数
    intro = request.POST.get('intro', None)
    img = request.FILES.get('img', None)
    # 查找企业
    enterprise = user.enterprise_user.enterprise
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    # 更新字段
    if intro:
        enterprise.intro = intro
    if img:
        img_url = 'enterprise' + str(user.id) + img.name
        with open('Static/' + img_url, 'wb') as f:
            for chunk in img.chunks():
                f.write(chunk)
        if not upload_file(img_url, 'Static/' + img_url):
            return response(code=SERVER_ERROR, msg='上传图片失败')
        enterprise.img_url = img_url
    enterprise.save()
    return response(msg='修改成功')
