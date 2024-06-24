from django.db import models
from user.models import User
from enterprise.models import Enterprise


# Create your models here.
class Activity(models.Model):
    user_id = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    enter_id = models.ForeignKey(to='enterprise.Enterprise', on_delete=models.CASCADE)
    # 源动态被删除时，这里应该不受影响，不能设置 on_delete=models.CASCADE / SET_NULL
    # 可以不用外键关联，直接存储源动态的 id
    from_act_id = models.ForeignKey(to='UserActivity', null=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    like = models.ManyToManyField(to='user.User', related_name='like_user_activity')


class Comment(models.Model):
    user_id = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    act_id = models.ForeignKey(to='UserActivity', on_delete=models.CASCADE)
    content = models.TextField()


class Message(models.Model):
    from_user_id = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    to_user_id = models.ForeignKey(to='user.User', on_delete=models.CASCADE)
    type = models.IntegerField(choices=((0, '系统消息'), (1, '点赞'), (2, '评论'), (3, '转发'), (4, '关注')), default=0)
    obj_id = models.CharField(max_length=10)
    title = models.CharField(max_length=50)
    content = models.TextField()

