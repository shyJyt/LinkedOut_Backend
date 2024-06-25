from django.db import models


# Create your models here.
class UserActivity(models.Model):
    user_id = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE)
    enter_id = models.ForeignKey(to='enterprise.Enterprise', on_delete=models.CASCADE)
    # 源动态被删除时，这里应该不受影响，不能设置 on_delete=models.CASCADE / SET_NULL
    # 可以不用外键关联，直接存储源动态的 id
    from_act_id = models.ForeignKey(to='self', on_delete=models.SET_NULL, null=True)
    is_forward = models.BooleanField(default=False)
    title = models.CharField(max_length=50)
    content = models.TextField()
    like = models.ManyToManyField(to='enterprise.User', related_name='like_user_activity')
    create_time = models.DateTimeField(auto_now_add=True)

    def to_string(self):
        return {
            'user_id': self.user_id.id,
            'enter_id': self.enter_id.id,
            'title': self.title,
            'content': self.content,
            'is_forward': self.is_forward,
            'likes': self.like.count(),
            'create_time': self.create_time,
        }


class Comment(models.Model):
    user_id = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE)
    act_id = models.ForeignKey(to='UserActivity', on_delete=models.CASCADE)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    from_user_id = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE, related_name='from_user')
    to_user_id = models.ForeignKey(to='enterprise.User', on_delete=models.CASCADE, related_name='to_user')
    type = models.IntegerField(choices=((0, '系统消息'), (1, '点赞'), (2, '评论'), (3, '转发'), (4, '关注')), default=0)
    obj_id = models.IntegerField(null=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)
