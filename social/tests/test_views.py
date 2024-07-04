from django.test import TestCase, Client
from django.urls import reverse
from social.models import UserActivity, Comment, Message
from enterprise.models import Enterprise, EnterpriseUser, User


class TestSocialViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(email='email1', nickname='user1', real_name='real_name', is_active=True, password='12345')
        self.enterprise = Enterprise.objects.create(name="Test Enterprise")
        # self.enterprise_user = EnterpriseUser.objects.create(user=self.user, enterprise=self.enterprise, role=0)
        self.user_activity = UserActivity.objects.create(user=self.user, enterprise=self.enterprise, title="Test Title",
                                                         content="Test Content")

    def login_user(self):
        url = reverse('login')
        response = self.client.post(url, {'email': 'email1', 'password': '12345'})
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue('token' in response_data['data'])
        self.token = response_data['data']['token']
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + self.token

    def test_publish_activity(self):
        self.login_user()
        response = self.client.post('/publish_activity/', {'title': 'New Activity', 'content': 'New Content'})
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json()['msg'], '动态发布成功！')

    def test_update_activity(self):
        self.login_user()
        activity = UserActivity.objects.create(user=self.user, title='Old Activity', content='Old Content')
        response = self.client.post('/update_activity/',
                                    {'activity_id': activity.id, 'title': 'Updated Activity',
                                     'content': 'Updated Content'})
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '动态更新成功！')

    def test_delete_activity(self):
        self.login_user()
        response = self.client.post(reverse('delete_activity'), {'activity_id': self.user_activity.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '动态删除成功！')

    def test_forward_activity(self):
        self.login_user()
        response = self.client.post(reverse('forward_activity'),
                                    {'title': 'Forwarded Title', 'content': 'Forwarded Content',
                                     'from_act_id': self.user_activity.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '动态发布成功！')

    def test_get_user_activity_list(self):
        response = self.client.get(reverse('get_user_activity_list'), {'user_id': self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '获取用户动态列表成功！')

    def test_get_enter_activity_list(self):
        response = self.client.get(reverse('get_enter_activity_list'), {'enter_id': self.enterprise.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '获取用户动态列表成功！')

    def test_like_activity(self):
        self.login_user()
        response = self.client.post(reverse('like_activity'), {'activity_id': self.user_activity.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '点赞成功！')

    def test_comment_activity(self):
        self.login_user()
        response = self.client.post(reverse('comment_activity'),
                                    {'activity_id': self.user_activity.id, 'content': 'Nice activity!'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '评论发布成功！')

    def test_update_comment(self):
        self.login_user()
        comment = Comment.objects.create(user=self.user, activity=self.user_activity, content="Original Comment")
        response = self.client.post(reverse('update_comment'), {'comment_id': comment.id, 'content': 'Updated Comment'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '评论发布成功！')

    def test_delete_comment(self):
        self.login_user()
        comment = Comment.objects.create(user=self.user, activity=self.user_activity, content="Original Comment")
        response = self.client.post(reverse('delete_comment'), {'comment_id': comment.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '评论删除成功！')

    def test_follow_user(self):
        other_user = User.objects.create(email='email2', nickname='user2', real_name='real_name', is_active=True, password='12345')
        url = reverse('login')
        response = self.client.post(url, {'email': 'email2', 'password': '12345'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('follow_user'), {'user_id': other_user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '关注成功！')

    def test_follow_enterprise(self):
        self.login_user()
        response = self.client.post(reverse('follow_enterprise'), {'enterprise_id': self.enterprise.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '关注成功！')

    def test_get_user_social_info(self):
        response = self.client.get(reverse('get_user_social_info'), {'user_id': self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '获取用户社交信息成功！')

    def test_get_message_list(self):
        self.login_user()
        response = self.client.get(reverse('get_message_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '获取消息列表成功！')

    def test_check_message(self):
        self.login_user()
        message = Message.objects.create(from_user=self.user, to_user=self.user, type=0, obj_id=1, title="Test Message",
                                         content="This is a test message")
        response = self.client.get(reverse('check_message'), {'message_id': message.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], '查看消息详情成功！')
