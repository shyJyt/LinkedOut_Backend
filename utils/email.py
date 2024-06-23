import random
from django.core.mail import send_mail
from config import BUAA_MAIL_USER


def send_email(email) -> int:
    """
    发送邮件
    :param email: 对方邮箱
    :return: 验证码
    """
    # 生成随机六位数验证码
    code = random.randint(100000, 999999)
    send_mail(
        "LinkedOut注册",
        f"欢迎注册LinkedOut平台,这是你的验证码:{code}",
        BUAA_MAIL_USER,
        [email],
    )
    return code
