from enterprise.models import Enterprise
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods


@allowed_methods(['GET'])
def searchEnterprise(request):
    """
    搜索企业
    用户搜索企业
    """
    name = request.GET.get('name', None)
    if not name:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    enterprise = Enterprise.objects.filter(name__contains=name)
    data = []
    for e in enterprise:
        data.append({
            'id': e.id,
            'name': e.name,
            'intro': e.intro,
            'img_url': e.img_url
        })
    return response(data=data)


@allowed_methods(['GET'])
def getEnterpriseInfo(request):
    """
    获取企业信息
    用户查看企业信息
    """
    enterprise_id = request.GET.get('enterprise_id', None)
    if not enterprise_id:
        return response(code=PARAMS_ERROR, msg='参数不完整')
    enterprise = Enterprise.objects.filter(id=enterprise_id).first()
    if not enterprise:
        return response(code=PARAMS_ERROR, msg='企业不存在')
    data = {
        'name': enterprise.name,
        'intro': enterprise.intro,
        'img_url': enterprise.img_url
    }
    return response(data=data)
