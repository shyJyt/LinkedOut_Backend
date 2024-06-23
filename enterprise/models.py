from django.db import models


# Create your models here.
class EnterpriseUser(models.Model):
    # 关联注册用户id
    user_id = models.ForeignKey('user.User', on_delete=models.CASCADE)
    # 关联企业id
    enterprise_id = models.ForeignKey('enterprise.Enterprise', on_delete=models.CASCADE)
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
