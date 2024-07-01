from django.urls import path

# from . import views
from .views.activity.interactions import *
from .views.activity.feeds import *
from .views.follow import *
from .views.message import *
from .views.chat import *

urlpatterns = [
    path('upload_image/', upload_image, name='upload_image'),
    path('publish_activity/', publish_activity, name='publish_activity'),
    path('update_activity/', update_activity, name='update_activity'),
    path('delete_activity/', delete_activity, name='delete_activity'),
    path('forward_activity/', forward_activity, name='forward_activity'),
    path('display_activity/', display_activity),
    path('get_user_activity_list/', get_user_activity_list, name='get_user_activity_list'),
    path('get_enter_activity_list/', get_enter_activity_list, name='get_enter_activity_list'),
    path('get_homepage_activity_list/', get_homepage_activity_list, name='get_homepage_activity_list'),
    path('like_activity/', like_activity, name='like_activity'),
    path('comment_activity/', comment_activity, name='comment_activity'),
    path('update_comment/', update_comment, name='update_comment'),
    path('delete_comment/', delete_comment, name='delete_comment'),
    path('get_user_social_info/', get_user_social_info, name='get_user_social_info'),
    path('get_message_list/', get_message_list, name='get_message_list'),
    path('check_message/', check_message, name='check_message'),
    path('follow_user/', follow_user, name='follow_user'),
    path('follow_enterprise/', follow_enterprise, name='follow_enterprise'),
    path('get_chat_history/', get_chat_history, name='get_chat_history'),
    path('get_chat_users/', get_chat_users, name='get_chat_users'),
]
