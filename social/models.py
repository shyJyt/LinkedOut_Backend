from django.db import models


# Create your models here.
class UserActivity(models.Model):
    user = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE)
    enterprise = models.ForeignKey(to='enterprise.Enterprise', on_delete=models.SET_NULL, null=True)
    # 源动态被删除时，这里应该不受影响，不能设置 on_delete=models.CASCADE / SET_NULL
    # 可以不用外键关联，直接存储源动态的 id
    from_act = models.ForeignKey(to='self', on_delete=models.SET_NULL, null=True)
    is_forward = models.BooleanField(default=False)
    title = models.CharField(max_length=50)
    content = models.TextField()
    images = models.JSONField(default=list)
    like = models.ManyToManyField(to='enterprise.User', related_name='like_user_activity')
    create_time = models.DateTimeField(auto_now_add=True)

    def to_string(self):
        return {
            'user_id': self.user.id,
            'enter_id': self.enterprise.id,
            'title': self.title,
            'content': self.content,
            'is_forward': self.is_forward,
            'likes': self.like.count(),
            'create_time': self.create_time,
        }


class Comment(models.Model):
    user = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE)
    activity = models.ForeignKey(to='UserActivity', on_delete=models.CASCADE)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    from_user = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE, related_name='to_user')
    type = models.IntegerField(choices=((0, '系统消息'), (1, '点赞'), (2, '评论'),
                                        (3, '转发'), (4, '关注'), (5, '邀请'),
                                        (6, '转让'), (7, '录用')
                                        ), default=0)
    obj_id = models.IntegerField(null=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    sender = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.message[:50]}'