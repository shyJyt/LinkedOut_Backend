from django.test import TestCase
from django.urls import reverse
from .models import Enterprise, EnterpriseUser, User, EnterpriseUser
from django.core.files.uploadedfile import SimpleUploadedFile


# Create your tests here.

class EnterpriseTestCase(TestCase):
    def setUp(self):
        self.account_api_prefix = '/api/enterprise'
        self.enterprise = Enterprise.objects.create(name="Test Enterprise")
        # 管理者
        self.manager = EnterpriseUser.objects.create(enterprise=self.enterprise,
                                                     role=0,
                                                     position='Test Position',
                                                     work_age='Test Work Age',
                                                     phone_number='Test Phone Number')
        self.manager_user = User.objects.create(email='182643720@qq.com',
                                                password='e9202a0accc6bd2fcd33ab2811a2c041',
                                                nickname='zh', enterprise_user=self.manager)
        # 员工
        self.employee = EnterpriseUser.objects.create(enterprise=self.enterprise,
                                                      role=1,
                                                      position='Test Position',
                                                      work_age='Test Work Age',
                                                      phone_number='Test Phone Number')
        self.employee_user = User.objects.create(email='182643721',
                                                 password='e9202a0accc6bd2fcd33ab2811a2c041',
                                                 nickname='zh', enterprise_user=self.employee)
        # 普通用户
        self.user = User.objects.create(email='182643722',
                                        password='e9202a0accc6bd2fcd33ab2811a2c041',
                                        nickname='zh')

    def test_create_enterprise(self):
        file = SimpleUploadedFile("test_file.txt", b"file_content")
        # 使用http的header里存储的token来验证用户身份
        response = self.client.post(self.account_api_prefix + '/createEnterprise',
                                    {
                                        'name': 'Test Enterprise',
                                        'intro': 'Test Enterprise Intro',
                                        'img': file,
                                    },
                                    headers={'token': '123'})

        self.assertEqual(response.status_code, 200)

    def test_add_employee(self):
        response = self.client.post(self.account_api_prefix + '/addEmployee',
                                    {
                                        'user_id': self.user.id,
                                    },
                                    headers={'token': '123'})
        self.assertEqual(response.status_code, 200)

    def test_update_enterprise_info(self):
        response = self.client.post(self.account_api_prefix + '/updateEnterpriseInfo',
                                    {
                                        'position': 'Test Position',
                                        'work_age': 'Test Work Age',
                                        'phone_number': 'Test Phone Number'
                                    },
                                    headers={'token': '123'})
        self.assertEqual(response.status_code, 200)

    def test_join_enterprise(self):
        response = self.client.post(self.account_api_prefix + '/joinEnterprise',
                                    {
                                        'enterprise_id': self.enterprise.id
                                    },
                                    headers={'token': '123'})
        self.assertEqual(response.status_code, 200)

    def test_complete_enterprise_info(self):
        response = self.client.post(self.account_api_prefix + '/completeEnterpriseInfo',
                                    {
                                        'position': 'Test Position',
                                        'work_age': 'Test Work Age',
                                        'phone_number': 'Test Phone Number'
                                    },
                                    headers={'token': '123'})
        self.assertEqual(response.status_code, 200)

    def test_exit_enterprise(self):
        response = self.client.post(self.account_api_prefix + '/exitEnterprise',
                                    {},
                                    headers={'token': '123'})
        self.assertEqual(response.status_code, 200)

    def test_expel_employee(self):
        response = self.client.post(self.account_api_prefix + '/expelEmployee',
                                    {
                                        'user_id': self.user.id
                                    },
                                    headers={'token': '123'})
        self.assertEqual(response.status_code, 200)
