from django.shortcuts import render

from enterprise.models import EnterpriseUser
from social.models import Activity
from utils.Response import response
from utils.view_decorator import allowed_methods, login_required


# Create your views here.
@allowed_methods(['POST'])
@login_required
def publish_activity(request):
    user = request.user
    try:
        enterprise_user = EnterpriseUser.objects.get(user_id=user.id)
        enterprise = enterprise_user.enterprise_id
    except EnterpriseUser.DoesNotExist:
        enterprise = None
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not title or not content:
        return response(PARAMS_ERROR, '请正确填入动态标题和内容！', error=True)
    Activity.objects.create(user_id=user, enter_id=enterprise, title=title, content=content)
    return response(SUCCESS, '动态发布成功！')


@allowed_methods(['POST'])
@login_required
def update_activity(request):
    user = request.user
    act_id = request.POST.get('activity_id')
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not title or not content:
        return response(PARAMS_ERROR, '请正确填入动态标题和内容！', error=True)
    try:
        activity = Activity.objects.get(act_id)
        if activity.user_id != user:
            return response(PARAMS_ERROR, '没用该动态更改权限！', error=True)
        activity.title = title
        activity.content = content
        activity.save()
    except Activity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '动态更新成功！')


@allowed_methods(['GET'])
@login_required
def delete_activity(request):
    user = request.user
    act_id = request.POST.get('activity_id')
    try:
        activity = Activity.objects.get(act_id)
        if activity.user_id != user:
            return response(PARAMS_ERROR, '没用该动态删除权限！', error=True)
        activity.delete()
    except Activity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '动态删除成功！')


@allowed_methods(['POST'])
@login_required
def forward_activity(request):
    user = request.user
    try:
        enterprise_user = EnterpriseUser.objects.get(user_id=user.id)
        enterprise = enterprise_user.enterprise_id
    except EnterpriseUser.DoesNotExist:
        enterprise = None
    title = request.POST.get('title')
    content = request.POST.get('content')
    from_act_id = request.POST.get('from_act_id')
    if not from_act_id:
        return response(PARAMS_ERROR, '转发动态不存在！', error=True)
    Activity.objects.create(user_id=user, enter_id=enterprise,from_act_id=from_act_id, title=title, content=content)
    return response(SUCCESS, '动态发布成功！')


@allowed_methods(['GET'])
def display_activity(request):
    act_id = request.POST.get('activity_id')
    try:
        activity = Activity.objects.get(act_id)
        data = [activity.to_string()]
        if activity.from_act_id:
            from_activity = Activity.objects.get(activity.from_act_id)
            data.append(from_activity)
    except Activity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '动态展示成功！', data=data)


@allowed_methods(['GET'])
def get_user_activity_list(request):
    user_id = request.GET.get('user_id')
    try:
        activities = Activity.objects.filter(user_id=user_id).values('id', 'title', 'content')
        activity_list = list(activities)
    except:
        return response(PARAMS_ERROR, '用户不存在！', error=True)
    return response(SUCCESS, '动态展示成功！', data=activity_list)


@allowed_methods(['GET'])
def get_enter_activity_list(request):
    enter_id = request.GET.get('enter_id')
    try:
        activities = Activity.objects.filter(enter_id=enter_id).values('id', 'title', 'content')
        activity_list = list(activities)
    except:
        return response(PARAMS_ERROR, '用户不存在！', error=True)
    return response(SUCCESS, '动态展示成功！', data=activity_list)