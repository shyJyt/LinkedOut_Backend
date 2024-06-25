from django.db import models

EDUCATION_CHOICES = ((0, '未知'),
                     (1, '本科以下'),
                     (2, '本科'),
                     (3, '硕士'),
                     (4, '博士'))


class User(models.Model):
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    real_name = models.CharField(max_length=50, null=True)
    nickname = models.CharField(max_length=50)
    age = models.IntegerField(default=None, null=True)
    avatar_key = models.CharField(max_length=50, default='')
    education = models.IntegerField(choices=EDUCATION_CHOICES, default=0)
    work_city = models.CharField(max_length=50, null=True)
    interested_post = models.ManyToManyField('enterprise.Post', related_name='interested_user')
    blog_link = models.CharField(max_length=100, null=True)
    github_link = models.CharField(max_length=100, null=True)
    resume_key = models.CharField(max_length=100, null=True)
    gpt_limit = models.IntegerField(default=10)

    enterprise_user = models.OneToOneField('enterprise.EnterpriseUser', on_delete=models.CASCADE, null=True,
                                           related_name='user')
    follow_enterprise = models.ManyToManyField('enterprise.Enterprise', related_name='enter_fans')
    follow_user = models.ManyToManyField('self')

    salt = models.CharField(max_length=4, default='')
    # 是否成功注册
    is_active = models.BooleanField(default=False)

    def to_string(self):
        return {
            'email': self.email,
            'real_name': self.real_name,
            'nickname': self.nickname,
            'age': self.age,
            'education': EDUCATION_CHOICES[self.education][1],
            'work_city': self.work_city,
            'interested_posts': [post.name for post in self.interested_post.all()],
            'blog_link': self.blog_link,
            'github_link': self.github_link,
            'gpt_limit': self.gpt_limit,
        }


class EnterpriseUser(models.Model):
    # 关联企业
    enterprise = models.ForeignKey('Enterprise', on_delete=models.CASCADE)
    # 管理者/员工,用枚举类型
    ROLE_CHOICES = (
        (0, 'manager'),
        (1, 'employee')
    )
    role = models.IntegerField(choices=ROLE_CHOICES, default=1)
    position = models.CharField(max_length=255, default='待完善')
    # 工龄
    work_age = models.CharField(max_length=255, default='待完善')
    phone_number = models.CharField(max_length=255, default='待完善')


class Post(models.Model):
    name = models.CharField(max_length=255)


class Enterprise(models.Model):
    # 企业名称
    name = models.CharField(max_length=255)
    # 企业简介
    intro = models.TextField()
    # 企业logo
    img_url = models.CharField(max_length=255)


class PostRecruitment(models.Model):
    # 关联企业
    enterprise = models.ForeignKey('Enterprise', on_delete=models.CASCADE)
    # 关联岗位
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    # 招聘人数
    recruit_number = models.CharField(max_length=255)
    # 工作地点
    work_place = models.CharField(max_length=255)
    # 薪资
    salary = models.CharField(max_length=255)
    # 要求
    requirement = models.TextField()
    # 工作内容
    work_content = models.TextField()
    # 工作经验
    work_experience = models.CharField(max_length=255)
    # 教育背景
    education = models.CharField(max_length=255)
    # 应聘人员,关联用户,一个岗位可以有多个应聘人员
    user = models.ManyToManyField('enterprise.User')
    # 已录用人员
    accepted_user = models.ManyToManyField('enterprise.User', related_name='be_accepted_post')


class Invitation(models.Model):
    # 邀请人
    from_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='invite')
    # 被邀请人
    to_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='be_invited')
    # 对象id
    obj_id = models.IntegerField()
    # 是否已经处理过
    is_handled = models.BooleanField(default=False)