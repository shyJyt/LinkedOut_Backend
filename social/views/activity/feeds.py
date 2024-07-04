from enterprise.models import User, Enterprise
from social.models import UserActivity, Comment
from utils.response import response
from utils.status_code import *
from utils.qos import get_file
from utils.view_decorator import allowed_methods, guest_and_user
from django.db.models import Count


@allowed_methods(['GET'])
@guest_and_user
def get_user_activity_list(request):
    """
    获取用户动态列表
    :param request: user_id
    :return: [code, msg, data] 其中data为发布动态者的头像，昵称，兴趣岗位，学历，动态发布时间，标题，内容，点赞收藏数，评论列表
    """
    user = request.user
    user_id = request.GET.get('user_id')
    try:
        check_user = User.objects.get(id=user_id)
        interested_posts = list(check_user.interested_post.values_list('name', flat=True))
    except User.DoesNotExist:
        return response(PARAMS_ERROR, '该用户不存在！', error=True)
    try:
        activities = UserActivity.objects.filter(user_id=user_id).order_by('-create_time')
    except UserActivity.DoesNotExist:
        return response(SUCCESS, '获取用户动态列表成功！', data=[])

    activity_list = []
    for activity in activities:
        # 动态的评论列表
        comments = Comment.objects.filter(activity_id=activity.id).order_by('-create_time')
        comment_list = [
            {
                'user_id': comment.user.id,
                'user_name': comment.user.nickname,
                'user_avatar': get_file(comment.user.avatar_key),
                'content': comment.content,
                'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for comment in comments
        ]
        activity_detail = {
            'activity_id': activity.id,
            'user_id': check_user.id,
            'user_avatar': get_file(check_user.avatar_key),
            'user_name': check_user.nickname,
            'education': check_user.get_education_display(),
            'interested_post': interested_posts,
            'title': activity.title,
            'content': activity.content,
            'likes': activity.like.count(),
            'is_like': False,
            'is_forward': activity.is_forward,
            'comment_num': comments.count(),
            'comment_list': comment_list,
            'create_time': activity.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if user and activity.like.filter(id=user.id).exists():
            activity_detail['is_like'] = True  # 如果用户已登录且点赞，is_like=True
        # 如果是转载动态，加入原动态信息from_activity
        if activity.is_forward:
            from_act = activity.from_act
            if from_act:
                from_activity = {
                    'id': from_act.id,
                    'user_id': from_act.user.id,
                    'user_name': from_act.user.nickname,
                    'user_avatar': get_file(from_act.user.avatar_key),
                    'title': from_act.title,
                    'content': from_act.content,
                    'create_time': from_act.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                activity_detail['from_activity'] = from_activity
            else:
                activity_detail['from_activity'] = None
        activity_list.append(activity_detail)
    '''
    interested_posts = list(check_user.interested_post.values_list('name', flat=True))
    data = {
        'user_avatar': check_user.avatar_key,
        'user_name': check_user.nickname,
        'education': check_user.get_education_display(),
        'interested_post': interested_posts,
        'activity_list': activity_list,
    }
    '''
    return response(SUCCESS, '获取用户动态列表成功！', data=activity_list)


@allowed_methods(['GET'])
@guest_and_user
def get_enter_activity_list(request):
    """
    获取企业动态列表，按员工影响力排序（按动态点赞数排序！）
    :param request: enter_id
    :return: [code, msg, data] 其中data为列表
    """
    user = request.user
    enter_id = request.GET.get('enter_id')
    if not enter_id:
        return response(PARAMS_ERROR, '请正确选择企业！', error=True)
    try:
        Enterprise.objects.get(id=enter_id)
    except Enterprise.DoesNotExist:
        return response(PARAMS_ERROR, '该企业不存在！', error=True)
    try:
        activities = UserActivity.objects.filter(enterprise_id=enter_id).order_by('-like')
    except UserActivity.DoesNotExist:
        return response(SUCCESS, '获取用户动态列表成功！', data=[])
    activity_list = []
    for activity in activities:
        # 动态发布者信息
        publisher = activity.user
        if publisher:
            publisher_info = {
                'user_id': publisher.id,
                'user_name': publisher.nickname,
                'user_avatar': get_file(publisher.avatar_key),
            }
        else:
            publisher_info = {}
        # 动态的评论列表
        comments = Comment.objects.filter(activity_id=activity.id).order_by('-create_time')
        comment_list = [
            {
                'user_id': comment.user.id,
                'user_name': comment.user.nickname,
                'user_avatar': get_file(comment.user.avatar_key),
                'content': comment.content,
                'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for comment in comments
        ]
        activity_detail = {
            'activity_id': activity.id,
            'publisher': publisher_info,
            'title': activity.title,
            'content': activity.content,
            'likes': activity.like.count(),
            'is_like': False,
            'is_forward': activity.is_forward,
            'comment_num': comments.count(),
            'comment_list': comment_list,
            'create_time': activity.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if user and activity.like.filter(id=user.id).exists():
            activity_detail['is_like'] = True  # 如果用户已登录且点赞，is_like=True
        # 如果是转载动态，加入原动态信息from_activity
        if activity.is_forward:
            from_act = activity.from_act
            if from_act:
                from_activity = {
                    'id': from_act.id,
                    'user_id': from_act.user.id,
                    'user_name': from_act.user.nickname,
                    'user_avatar': get_file(from_act.user.avatar_key),
                    'title': from_act.title,
                    'content': from_act.content,
                    'create_time': from_act.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                activity_detail['from_activity'] = from_activity
            else:
                activity_detail['from_activity'] = None
        activity_list.append(activity_detail)
    return response(SUCCESS, '获取用户动态列表成功！', data=activity_list)


@allowed_methods(['GET'])
@guest_and_user
def get_homepage_activity_list(request):
    """
    获取首页推荐动态列表
    :param request: user_id
    :return: [code, msg, data] 其中data为发布动态者的头像，昵称，兴趣岗位，学历，动态发布时间，标题，内容，点赞收藏数，评论列表
    """
    user = request.user
    if user:
        followed_users_activities = UserActivity.objects.filter(user__in=user.follow_user.all())
        followed_enterprises_activities = UserActivity.objects.filter(enterprise__in=user.follow_enterprise.all())
        high_like_activities = UserActivity.objects.annotate(like_count=Count('like')).order_by('-like_count')
        activities = followed_users_activities | followed_enterprises_activities | high_like_activities
        activities = activities.distinct().annotate(like_count=Count('like')).order_by('-like_count')[:10]
    else:
        activities = UserActivity.objects.annotate(like_count=Count('like')).order_by('-like_count')[:10]

    activity_list = []
    for activity in activities:
        # 动态发布者信息
        publisher = activity.user
        if publisher:
            publisher_info = {
                'user_id': publisher.id,
                'user_name': publisher.nickname,
                'user_avatar': get_file(publisher.avatar_key),
            }
        else:
            publisher_info = {}
        # 动态的评论列表
        comments = Comment.objects.filter(activity_id=activity.id).order_by('-create_time')

        activity_detail = {
            'activity_id': activity.id,
            'publisher': publisher_info,
            'title': activity.title,
            'content': activity.content,
            'likes': activity.like.count(),
            'is_like': False,
            'is_forward': activity.is_forward,
            'comment_num': comments.count(),
            'create_time': activity.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if user and activity.like.filter(id=user.id).exists():
            activity_detail['is_like'] = True  # 如果用户已登录且点赞，is_like=True
        # 如果是转载动态，加入原动态信息from_activity
        if activity.is_forward:
            from_act = activity.from_act
            if from_act:
                from_activity = {
                    'id': from_act.id,
                    'user_id': from_act.user.id,
                    'user_name': from_act.user.nickname,
                    'user_avatar': get_file(from_act.user.avatar_key),
                    'title': from_act.title,
                    'content': from_act.content,
                    'create_time': from_act.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                activity_detail['from_activity'] = from_activity
            else:
                activity_detail['from_activity'] = None
        activity_list.append(activity_detail)
    return response(SUCCESS, '获取首页推荐动态列表成功！', data=activity_list)


@allowed_methods(['GET'])
@guest_and_user
def display_activity(request):
    """
    获取动态详情
    :param request: activity_id
    :return: [code, msg, data] 其中data为动态详情
    """
    user = request.user
    act_id = request.GET.get('activity_id')
    try:
        activity = UserActivity.objects.get(id=act_id)
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    # 动态发布者信息
    publisher = activity.user
    if publisher:
        publisher_info = {
            'user_id': publisher.id,
            'user_name': publisher.nickname,
            'user_avatar': get_file(publisher.avatar_key),
        }
    else:
        publisher_info = {}
    # 动态评论信息
    comments = Comment.objects.filter(activity_id=act_id).order_by('-create_time')
    comment_list = [
        {
            'user_id': comment.user.id,
            'user_name': comment.user.nickname,
            'user_avatar': get_file(comment.user.avatar_key),
            'content': comment.content,
            'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for comment in comments
    ]
    data = {
        'activity_id': activity.id,
        'publisher': publisher_info,
        'title': activity.title,
        'content': activity.content,
        'likes': activity.like.count(),
        'is_like': False,
        'is_forward': activity.is_forward,
        'comment_num': comments.count(),
        'comment_list': comment_list,
        'create_time': activity.create_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    # 用户点赞情况
    if user and activity.like.filter(id=user.id).exists():
        data['is_like'] = True  # 如果用户已登录且点赞，is_like=True
    # 如果评论是转发评论
    if activity.is_forward:
        from_act = activity.from_act
        if from_act:
            from_activity = {
                'id': from_act.id,
                'user_id': from_act.user.id,
                'user_name': from_act.user.nickname,
                'user_avatar': get_file(from_act.user.avatar_key),
                'title': from_act.title,
                'content': from_act.content,
                'create_time': from_act.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            data['from_activity'] = from_activity
        else:
            data['from_activity'] = None

    return response(SUCCESS, '动态展示成功！', data=data)
