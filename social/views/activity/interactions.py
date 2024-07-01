import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import IntegrityError

from enterprise.models import User, EnterpriseUser, Enterprise, Invitation, Transfer, PostRecruitment
from social.models import UserActivity, Comment, Message
from social.views.message import send_message
from utils.qos import get_file, generate_time_stamp
from utils.response import response
from utils.status_code import *
from utils.qos import get_file, save_file_local, upload_file
from utils.view_decorator import allowed_methods, login_required, guest_and_user


# Create your views here.
@allowed_methods(['POST'])
@login_required
def upload_image(request):
    """
    上传动态图片
    :param request: title, content
    :return: [code, msg]
    """
    user = request.user
    image = request.FILES.get('image')

    if image:
        local_file = save_file_local(image)
        key = f"{user.id}_embedded_image_{generate_time_stamp()}.png"
        ret = upload_file(key, local_file)
        os.remove(local_file)
        if ret:
            return response(SUCCESS, '图片上传成功！', data=get_file(key))
        else:
            return response(OSS_ERROR, '图片上传失败！', error=True)


@allowed_methods(['POST'])
@login_required
def publish_activity(request):
    """
    发表动态
    :param request: title, content
    :return: [code, msg]
    """
    user = request.user
    user: User
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
        if title:
            activity.title = title
        if content:
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
                    send_message(user, activity.user, 0, act_id, '系统通知',
                                 f'企业管理员 {user.nickname} 删除了你的动态')
                    # 给被删除动态的用户发送消息
                    deleted_id = activity.user.id
                    group_room_name = f'system_message_{deleted_id}'
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        group_room_name,
                        {
                            'type': 'send_message',
                            'message': f'企业管理员 {user.nickname} 删除了你的动态',
                        }
                    )
                    activity.delete()
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
            from_user = from_act.user
        # from_act是转发动态
        else:
            from_user = from_act.from_act.user
        UserActivity.objects.create(user=user, enterprise=enterprise, from_act=from_act, is_forward=True,
                                    title=title, content=content)
        send_message(user, from_user, 3, from_act.id, '转发', f'用户 {user.nickname} 转发了你的动态')
        # 给被转载的用户发送消息
        forwarded_id = from_user.id
        group_room_name = f'system_message_{forwarded_id}'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_room_name,
            {
                'type': 'send_message',
                'message': f'用户 {user.nickname} 转发了你的动态',
            }
        )
    except UserActivity.DoesNotExist:
        return response(PARAMS_ERROR, '转发动态不存在！', error=True)
    return response(SUCCESS, '动态发布成功！')


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
            # 给被点赞的用户发送消息
            liked_id = activity.user.id
            group_room_name = f'system_message_{liked_id}'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                group_room_name,
                {
                    'type': 'send_message',
                    'message': f'用户 {user.nickname} 点赞了你的动态',
                }
            )
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
        # 给被评论的用户发送消息
        commented_id = activity.user.id
        group_room_name = f'system_message_{commented_id}'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_room_name,
            {
                'type': 'send_message',
                'message': f'用户 {user.nickname} 评论了你的动态',
            }
        )
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
                    send_message(user, comment.user, 0, comment_id, '系统通知', f'企业管理员 {user.nickname} 删除了你的评论')
                    # 给被删除评论的用户发送消息
                    deleted_id = comment.user.id
                    group_room_name = f'system_message_{deleted_id}'
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        group_room_name,
                        {
                            'type': 'send_message',
                            'message': f'企业管理员 {user.nickname} 删除了你的评论',
                        }
                    )
                    comment.delete()
                else:
                    return response(PARAMS_ERROR, '无删除权限！', error=True)
            except EnterpriseUser.DoesNotExist:
                return response(PARAMS_ERROR, '无删除权限！', error=True)
    except Comment.DoesNotExist:
        return response(PARAMS_ERROR, '评论不存在！', error=True)
    return response(SUCCESS, '评论删除成功！')


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
            'avatar_key': get_file(following.avatar_key),
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
