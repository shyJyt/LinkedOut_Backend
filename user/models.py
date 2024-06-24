from django.db import models


# Create your models here.

class User(models.Model):
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    real_name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50)
    avatar_key = models.CharField(max_length=50, default='')
    education = models.IntegerField(choices=((0, '未知'), (1, '本科以下'), (2, '本科'), (3, '硕士'), (4, '博士')),
                                    default=0)
    work_city = models.CharField(max_length=50)
    interested_post = models.ManyToManyField('enterprise.Post', related_name='interested_user')
    blog_link = models.CharField(max_length=100)
    github_link = models.CharField(max_length=100)
    resume_url = models.CharField(max_length=100)
    gpt_limit = models.IntegerField(default=10)

    enterprise_user = models.OneToOneField('enterprise.EnterpriseUser', on_delete=models.CASCADE, null=True)
    follow_enterprise = models.ManyToManyField('enterprise.Enterprise', related_name='follow_user')
    follow_user = models.ManyToManyField('self', related_name='follow_user')

    salt = models.CharField(max_length=4, default='')
    # 是否成功注册
    is_active = models.BooleanField(default=False)

    def to_string(self):
        return {
            'nickname': self.nickname,
            'real_name': self.real_name,
            'interested_posts': [post.name for post in self.interested_post.all()],
        }
