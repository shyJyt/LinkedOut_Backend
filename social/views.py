from django.db import IntegrityError
from django.shortcuts import render

from utils.response import response
from utils.status_code import *
from utils.view_decorator import allowed_methods, login_required, guest_and_user
from enterprise.models import User, EnterpriseUser, Enterprise
from social.models import UserActivity, Comment, Message


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
    enterprise_user = user.enterprise_user
    if enterprise_user and enterprise_user.enterprise:
        enterprise = enterprise_user.enterprise
    else:
        enterprise = None

    title = request.POST.get('title')
    content = request.POST.get('content')
    if not title or not content:
        return response(PARAMS_ERROR, '请正确填入动态标题和内容！', error=True)
    UserActivity.objects.create(user=user, enterprise=enterprise, title=title, content=content)
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
        activity = UserActivity.objects.get(id=act_id)
        if activity.user != user:
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
    删除动态 （动态发布者、动态对应企业管理员）
    :param request: activity_id
    :return: [code, msg]
    """
    user = request.user
    act_id = request.POST.get('activity_id')
    try:
        activity = UserActivity.objects.get(id=act_id)
        # 当前用户是动态发布者
        if activity.user == user:
            activity.delete()
        else:
            try:
                enterprise_user = EnterpriseUser.objects.get(user=user)
                # 当前用户是该动态对应企业的管理员
                if enterprise_user.role == 0 and enterprise_user.enterprise == activity.enter_id:
                    activity.delete()
                    send_message(user, activity.user, 0, act_id, '系统通知', f'企业管理员 {user.nickname} 删除了你的动态')
                else:
                    return response(PARAMS_ERROR, '没用该动态删除权限！', error=True)
            except EnterpriseUser.DoesNotExist:
                return response(PARAMS_ERROR, '没用该动态删除权限！', error=True)
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
    enterprise_user = user.enterprise_user
    if enterprise_user and enterprise_user.enterprise:
        enterprise = enterprise_user.enterprise
    else:
        enterprise = None
    title = request.POST.get('title')
    content = request.POST.get('content')
    from_act_id = request.POST.get('from_act_id')
    if not from_act_id:
        return response(PARAMS_ERROR, '未选择待转发动态！', error=True)
    try:
        from_act = UserActivity.objects.get(id=from_act_id)
        # from_act是原创
        if not from_act.is_forward:
            UserActivity.objects.create(user=user, enterprise=enterprise, from_act=from_act, is_forward=True,
                                        title=title, content=content)
            send_message(user, from_act.user, 3, from_act.id, '转发', f'用户 {user.nickname} 转发了你的动态')
        # from_act是转发动态
        else:
            UserActivity.objects.create(user=user, enterprise=enterprise, from_act=from_act.from_act_id,
                                        is_forward=True, title=title, content=content)
            send_message(user, from_act.from_act.user, 3, from_act.from_act.id, '转发', f'用户 {user.nickname} 转发了你的动态')
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '转发动态不存在！', error=True)
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
        if activity.is_forward:
            try:
                from_activity = activity.from_act_id
                data.append(from_activity.to_string())
            except UserActivity.DoesNotExist:
                data.append([])
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '动态展示成功！', data=data)


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
        activities = UserActivity.objects.filter(user_id=user_id).order_by('create_time')
    except UserActivity.DoesNotExist:
        activity_list = []
    activity_list = []
    for activity in activities:
        # 动态的评论列表
        comments = Comment.objects.filter(activity_id=activity.id).order_by('create_time')
        comment_list = [
            {
                'user_id': comment.user.id,
                'user_name': comment.user.nickname,
                'user_avatar': comment.user.avatar_key,
                'content': comment.content,
                'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for comment in comments
        ]
        activity_detail = {
            'activity_id': activity.id,
            'user_avatar': check_user.avatar_key,
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
                    'user_avatar': from_act.user.avatar_key,
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
        enterprise = Enterprise.objects.get(id=enter_id)
    except Enterprise.DoesNotExist:
        return response(PARAMS_ERROR, '该企业不存在！', error=True)
    try:
        activities = UserActivity.objects.filter(enterprise_id=enter_id).order_by('-like')
    except UserActivity.DoesNotExist:
        activity_list = []
    activity_list = []
    for activity in activities:
        # 动态发布者信息
        publisher = activity.user
        if publisher:
            publisher_info = {
                'user_id': publisher.id,
                'user_name': publisher.nickname,
                'user_avatar': publisher.avatar_key,
            }
        else:
            publisher_info = {}
        # 动态的评论列表
        comments = Comment.objects.filter(activity_id=activity.id).order_by('create_time')
        comment_list = [
            {
                'user_id': comment.user.id,
                'user_name': comment.user.nickname,
                'user_avatar': comment.user.avatar_key,
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
                    'user_avatar': from_act.user.avatar_key,
                    'title': from_act.title,
                    'content': from_act.content,
                    'create_time': from_act.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                activity_detail['from_activity'] = from_activity
            else:
                activity_detail['from_activity'] = None
        activity_list.append(activity_detail)
    return response(SUCCESS, '获取用户动态列表成功！', data=activity_list)


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
        activity = UserActivity.objects.get(id=act_id)
        if user in activity.like.all():  # 如果like为空就点赞
            activity.like.remove(user)
            msg = '取消点赞成功！'
        else:
            activity.like.add(user)
            msg = '点赞成功！'
            send_message(user, activity.user, 1, activity.id, '点赞', f'用户 {user.nickname} 点赞了你的动态')
        activity.save()
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '点赞动态不存在！', error=True)
    return response(SUCCESS, msg)


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
        activity = UserActivity.objects.get(id=act_id)
        Comment.objects.create(user=user, activity=activity, content=content)
        send_message(user, activity.user, 2, activity.id, '评论', f'用户 {user.nickname} 评论了你的动态')
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '动态不存在！', error=True)
    return response(SUCCESS, '评论发布成功！')


@allowed_methods(['POST'])
@login_required
def update_comment(request):
    """
    编辑评论
    :param request: comment_id, content
    :return: [code, msg]
    """
    user = request.user
    comment_id = request.POST.get('comment_id')
    content = request.POST.get('content')
    try:
        comment = Comment.objects.get(id=comment_id)
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
    删除评论 （发布评论的人、企业管理员）
    :param request: content_id
    :return: [code, msg]
    """
    user = request.user
    comment_id = request.POST.get('comment_id')
    try:
        comment = Comment.objects.get(id=comment_id)
        # 当前用户是评论发布者
        if comment.user_id == user.id:
            comment.delete()
        else:
            try:
                enterprise_user = EnterpriseUser.objects.get(user=user)
                # 当前用户是评论动态对应企业的管理员
                if enterprise_user.role == 0 and enterprise_user.enterprise == comment.act_id.enter_id:
                    comment.delete()
                    send_message(user, comment.user, 0, comment_id, '系统通知',
                                 f'企业管理员 {user.nickname} 删除了你的评论')
                else:
                    return response(PARAMS_ERROR, '无删除权限！', error=True)
            except EnterpriseUser.DoesNotExist:
                return response(PARAMS_ERROR, '无删除权限！', error=True)
    except Comment.DoesNotExist:
        return response(PARAMS_ERROR, '评论不存在！', error=True)
    return response(SUCCESS, '评论删除成功！')


@allowed_methods(['POST'])
@login_required
def follow_user(request):
    """
    关注用户/取消关注
    :param request: user_id
    :return: [code, msg]
    """
    user = request.user
    user_id = request.POST.get('user_id')
    try:
        user_id = int(user_id)
    except ValueError:
        return response(PARAMS_ERROR, '无效的用户ID！', error=True)
    if user_id == user.id:
        return response(PARAMS_ERROR, '用户不能关注自己！', error=True)
    try:
        following = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response(PARAMS_ERROR, '该用户不存在！', error=True)
    if following in user.follow_user.all():
        user.follow_user.remove(following)
        msg = '取消关注！'
    else:
        user.follow_user.add(following)
        msg = '关注成功！'
    user.save()
    return response(SUCCESS, msg)


@allowed_methods(['POST'])
@login_required
def follow_enterprise(request):
    """
    关注企业
    :param request: enterprise_id
    :return: [code, msg]
    """
    user = request.user
    enter_id = request.POST.get('enterprise_id')
    try:
        following = Enterprise.objects.get(id=enter_id)
    except Enterprise.DoesNotExist:
        return response(PARAMS_ERROR, '该企业不存在！', error=True)
    if following in user.follow_enterprise.all():
        user.follow_enterprise.remove(following)
        msg = '取消关注！'
    else:
        user.follow_enterprise.add(following)
        msg = '关注成功！'
    user.save()
    return response(SUCCESS, msg)


@allowed_methods(['GET'])
@guest_and_user
def get_user_social_info(request):
    """
    获取用户社交信息
    :param request: user_id
    :return: [code, msg, data] 获赞数，关注数，粉丝数，关注列表
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return response(PARAMS_ERROR, '未提供用户ID', error=True)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response(PARAMS_ERROR, '用户不存在！', error=True)

    liked_activities = UserActivity.objects.filter(user_id=user_id)
    total_likes = sum(activity.like.count() for activity in liked_activities)

    following_count = user.follow_user.count()
    followers_count = User.objects.filter(follow_user__id=user_id).count()

    followings = user.follow_user.all()
    following_list = []

    for following in followings:
        interested_posts = list(following.interested_post.values_list('name', flat=True))
        liked_activities = UserActivity.objects.filter(user_id=following.id)
        likes = sum(activity.like.count() for activity in liked_activities)
        followers = User.objects.filter(follow_user__id=following.id).count()
        following_info = {
            'id': following.id,
            'nickname': following.nickname,
            'avatar_key': following.avatar_key,
            'education': following.get_education_display(),
            'interested_post': interested_posts,
            'total_likes': likes,
            'followers_count': followers,
        }
        following_list.append(following_info)

    data = {
        'total_likes': total_likes,
        'following_count': following_count,
        'followers_count': followers_count,
        'following_list': following_list
    }
    return response(SUCCESS, '获取用户社交信息成功！', data=data)


def send_message(from_user, to_user, msg_type, obj_id, title, content):
    """
    发送系统通知（动态交互、员工变更等）
    :param : from_user, to_user, type, obj_id, title, content
    :return: 是否成功
    """
    try:
        message = Message(
            from_user=from_user,
            to_user=to_user,
            type=msg_type,
            obj_id=obj_id,
            title=title,
            content=content
        )
        message.save()
        return True
    except IntegrityError:
        return False


@allowed_methods(['GET'])
@login_required
def get_message_list(request):
    """
    获取用户消息列表
    :param request:
    :return: [code, msg, data]
    """
    user = request.user
    try:
        messages = Message.objects.filter(to_user=user).order_by('-create_time')
        message_list = [
            {
                'from_user': message.from_user.nickname,
                'type': message.get_type_display(),
                'title': message.title,
                'content': message.content,
                'is_read': message.is_read,
                'create_time': message.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for message in messages
        ]
        return response(SUCCESS, '获取消息列表成功！', data=message_list)
    except Exception as e:
        return response(SERVER_ERROR, '获取消息列表失败！', error=True)


@allowed_methods(['GET'])
@login_required
def check_message(request):
    """
    查看消息详情
    :param request: message_id
    :return: [code, msg, data]
    """
    user = request.user
    message_id = request.GET.get('message_id')
    try:
        message = Message.objects.get(id=message_id)
        if message.to_user.id != user.id:
            return response(PARAMS_ERROR, '无查看权限！', error=True)
        message_detail = {
            'from_user': message.from_user.nickname,
            'type': message.get_type_display(),
            'obj_id': message.obj_id,
            'title': message.title,
            'content': message.content,
            'create_time': message.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if not message.is_read:
            message.is_read = True
            message.save()
        return response(SUCCESS, '查看消息详情成功！', data=message_detail)
    except Message.DoesNotExist:
        return response(PARAMS_ERROR, '消息不存在！', error=True)
