from django.db import models


# Create your models here.
class EnterpriseUser(models.Model):
    # 关联注册用户
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
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
    work_age = models.IntegerField(default=0)
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
    user = models.ManyToManyField('user.User')
