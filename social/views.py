from django.shortcuts import render
from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, login_required
from enterprise.models import EnterpriseUser
from social.models import UserActivity, Comment


# Create your views here.
@allowed_methods(['POST'])
@login_required
def publish_activity(request):
    """
    发表动态
    :param request: title, content
    :return: [code, msg]
    """
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
    UserActivity.objects.create(user_id=user, enter_id=enterprise, title=title, content=content)
    return response(SUCCESS, '动态发布成功！')


@allowed_methods(['POST'])
@login_required
def update_activity(request):
    """
    更新动态
    :param request: activity_id, title, content
    :return: [code, msg]
    """
    user = request.user
    act_id = request.POST.get('activity_id')
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not title or not content:
        return response(PARAMS_ERROR, '请正确填入动态标题和内容！', error=True)
    try:
        activity = UserActivity.objects.get(act_id)
        if activity.user_id != user:
            return response(PARAMS_ERROR, '没用该动态更改权限！', error=True)
        activity.title = title
        activity.content = content
        activity.save()
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '动态更新成功！')


@allowed_methods(['POST'])
@login_required
def delete_activity(request):
    """
    删除动态
    :param request: activity_id
    :return: [code, msg]
    """
    # TODO: 企业管理员是否可以删除动态
    user = request.user
    act_id = request.POST.get('activity_id')
    try:
        activity = UserActivity.objects.get(act_id)
        if activity.user_id != user:
            return response(PARAMS_ERROR, '没用该动态删除权限！', error=True)
        activity.delete()
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '动态删除成功！')


@allowed_methods(['POST'])
@login_required
def forward_activity(request):
    """
    转发动态
    :param request: title, content, from_act_id
    :return: [code, msg]
    """
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
    UserActivity.objects.create(user_id=user, enter_id=enterprise, from_act_id=from_act_id, title=title, content=content)
    return response(SUCCESS, '动态发布成功！')


@allowed_methods(['GET'])
def display_activity(request):
    """
    获取动态详情
    :param request: activity_id
    :return: [code, msg, data] 其中data为动态详情
    """
    act_id = request.POST.get('activity_id')
    try:
        activity = UserActivity.objects.get(act_id)
        data = [activity.to_string()]
        if activity.from_act_id:
            from_activity = UserActivity.objects.get(activity.from_act_id)
            data.append(from_activity.to_string())
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '动态展示成功！', data=data)


@allowed_methods(['GET'])
def get_user_activity_list(request):
    """
    获取用户动态列表
    :param request: user_id
    :return: [code, msg, data] 其中data为列表
    """
    user_id = request.GET.get('user_id')
    try:
        activities = UserActivity.objects.filter(user_id=user_id).values('id', 'title', 'content')
        activity_list = list(activities)
    except:
        return response(PARAMS_ERROR, '用户不存在！', error=True)
    return response(SUCCESS, '动态展示成功！', data=activity_list)


@allowed_methods(['GET'])
def get_enter_activity_list(request):
    """
    获取企业动态列表
    :param request: enter_id
    :return: [code, msg, data] 其中data为列表
    """
    # TODO: 按员工影响力排序
    enter_id = request.GET.get('enter_id')
    try:
        activities = UserActivity.objects.filter(enter_id=enter_id).values('id', 'title', 'content')
        activity_list = list(activities)
    except:
        return response(PARAMS_ERROR, '企业不存在！', error=True)
    return response(SUCCESS, '动态展示成功！', data=activity_list)


@allowed_methods(['POST'])
@login_required
def like_activity(request):
    """
    点赞动态/取消点赞
    :param request: activity_id
    :return: [code, msg]
    """
    user = request.user
    act_id = request.POST.get('activity_id')
    try:
        activity = UserActivity.objects.get(act_id)
        like = activity.like.get(id=user.id)
        if not like:   # 如果like为空就点赞
            activity.like.add(user)
        else:          # 如果like不为空就取消点赞
            activity.like.remove(user)
        activity.save()
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '点赞动态不存在！', error=True)
    return response(SUCCESS, '点赞成功！')


@allowed_methods(['POST'])
@login_required
def comment_activity(request):
    """
    评论动态
    :param request: activity_id, content
    :return: [code, msg]
    """
    user = request.user
    act_id = request.POST.get('activity_id')
    content = request.POST.get('content')
    try:
        activity = UserActivity.objects.get(act_id)
        Comment.objects.create(user_id=user.id, act_id=activity, content=content)
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '评论发布成功！')


@allowed_methods(['POST'])
@login_required
def update_comment(request):
    """
    编辑评论
    :param request: content_id, content
    :return: [code, msg]
    """
    user = request.user
    comment_id = request.POST.get('comment_id')
    content = request.POST.get('content')
    try:
        comment = Comment.objects.get(comment_id)
        if comment.user_id != user.id:
            return response(PARAMS_ERROR, '无编辑权限！', error=True)
        comment.content = content
        comment.save()
    except Comment.DoesNotExist:
        return response(PARAMS_ERROR, '评论不存在！', error=True)
    return response(SUCCESS, '评论发布成功！')


@allowed_methods(['POST'])
@login_required
def delete_comment(request):
    """
    删除评论 （发布评论的人、发布动态的人？，企业管理员？）
    :param request: content_id
    :return: [code, msg]
    """
    # TODO: 发布动态的人和企业管理员是否可以删除评论
    user = request.user
    comment_id = request.POST.get('comment_id')
    try:
        comment = Comment.objects.get(comment_id)
        if comment.user_id != user.id:
            return response(PARAMS_ERROR, '无删除权限！', error=True)
        comment.delete()
    except Comment.DoesNotExist:
        return response(PARAMS_ERROR, '评论不存在！', error=True)
    return response(SUCCESS, '评论发布成功！')
