from django.test import TestCase

# Create your tests here.

user_api_prefix = '/api/user'

class TestAccount(TestCase):
    def test_register(self):
        response = self.client.post(user_api_prefix + '/register',
                                    {'nickname': 'test', 
                                     'real_name': 'test',
                                     'email': '21371337@buaa.edu.cn',
                                     'password': 'test',
                                     'password_repeat': 'test'})
        
        self.assertEqual(response.status_code, 200)
    
    def test_login(self):
        response = self.client.post(user_api_prefix + '/login',
                                    {'email': '21371337@buaa.edu.cn',
                                     'password': 'test'})
        
        self.assertEqual(response.status_code, 200)

    def test_active_user(self):
        response = self.client.post(user_api_prefix + '/activeUser',
                                    {'correct_code': 'test',
                                     'get_code': 'test',
                                     'email': '21371337@buaa.edu.cn'})
                                     

class TestUserInfo(TestCase):
    def test_update_user_info(self):
        response = self.client.post(user_api_prefix + '/changeInfo',
                                    data={'nickname': 'test', 
                                     'real_name': 'test',
                                     'age': '20',
                                     'education': '1',
                                     'email': '21371337@buaa.edu.cn'},
                                    headers={'token': '123'})
        
        self.assertEqual(response.status_code, 200)
    
    def test_get_user_info(self):
        response = self.client.get(user_api_prefix + '/getUserInfo',
                                    headers={'token': '123'})
        
        self.assertEqual(response.status_code, 200)

    def test_get_user_info_by_id(self):
        response = self.client.get(user_api_prefix + '/getUserInfoById',
                                    data={'user_id': '1'},
                                    headers={'token': '123'})
        
        self.assertEqual(response.status_code, 200)
                                     

