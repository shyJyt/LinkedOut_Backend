from django.test import TestCase
from enterprise.models import Enterprise, User
from social.models import UserActivity, Comment, Message


# Create your tests here.

class TestSocialModels(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create(email='email1', nickname='user1', real_name='real_name', is_active=True)
        self.user2 = User.objects.create(email='email2', nickname='user2', real_name='real_name', is_active=True)

        # 创建测试企业
        self.enterprise = Enterprise.objects.create(name='Test Enterprise')

        # 创建 UserActivity 实例
        self.activity = UserActivity.objects.create(
            user=self.user1,
            enterprise=self.enterprise,
            title='Test Activity',
            content='This is a test activity'
        )

    def test_user_activity_creation(self):
        # 测试 UserActivity 是否正确创建
        activity = UserActivity.objects.get(id=self.activity.id)
        self.assertEqual(activity.title, 'Test Activity')
        self.assertEqual(activity.content, 'This is a test activity')
        self.assertFalse(activity.is_forward)
        self.assertEqual(activity.user, self.user1)
        self.assertEqual(activity.enterprise, self.enterprise)

    def test_comment_creation(self):
        # 测试 Comment 是否正确创建
        comment = Comment.objects.create(
            user=self.user2,
            activity=self.activity,
            content='This is a test comment'
        )
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.user, self.user2)
        self.assertEqual(comment.activity, self.activity)

    def test_message_creation(self):
        # 测试 Message 是否正确创建
        message = Message.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            type=1,  # 点赞类型
            obj_id=self.activity.id,
            title='Test Message',
            content='This is a test message'
        )
        self.assertEqual(message.from_user, self.user1)
        self.assertEqual(message.to_user, self.user2)
        self.assertEqual(message.type, 1)
        self.assertEqual(message.obj_id, self.activity.id)
        self.assertEqual(message.title, 'Test Message')
        self.assertEqual(message.content, 'This is a test message')
        self.assertFalse(message.is_read)

    def test_user_activity_to_string(self):
        # 测试 UserActivity 的 to_string 方法
        expected_output = {
            'user_id': self.user1.id,
            'enter_id': self.enterprise.id,
            'title': 'Test Activity',
            'content': 'This is a test activity',
            'is_forward': False,
            'likes': 0,
            'create_time': self.activity.create_time,
        }
        self.assertEqual(self.activity.to_string(), expected_output)
