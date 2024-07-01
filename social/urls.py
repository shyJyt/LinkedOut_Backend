from django.urls import path

from . import views

urlpatterns = [
    path('upload_image/', views.upload_image, name='upload_image'),
    path('publish_activity/', views.publish_activity, name='publish_activity'),
    path('update_activity/', views.update_activity, name='update_activity'),
    path('delete_activity/', views.delete_activity, name='delete_activity'),
    path('forward_activity/', views.forward_activity, name='forward_activity'),
    # path('display_activity/', views.display_activity),
    path('get_user_activity_list/', views.get_user_activity_list, name='get_user_activity_list'),
    path('get_enter_activity_list/', views.get_enter_activity_list, name='get_enter_activity_list'),
    path('like_activity/', views.like_activity, name='like_activity'),
    path('comment_activity/', views.comment_activity, name='comment_activity'),
    path('update_comment/', views.update_comment, name='update_comment'),
    path('delete_comment/', views.delete_comment, name='delete_comment'),
    path('get_message_list/', views.get_message_list, name='get_message_list'),
    path('check_message/', views.check_message, name='check_message'),
    path('follow_user/', views.follow_user, name='follow_user'),
    path('get_user_social_info/', views.get_user_social_info, name='get_user_social_info'),
    path('follow_enterprise/', views.follow_enterprise, name='follow_enterprise'),
]
