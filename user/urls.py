from django.urls import path
from .views import account, user_info, recommend, search, others

urlpatterns = [
    path('register', account.register),
    path('login', account.login),
    path('activeUser', account.active_user),
    path('unsubscribe', account.unsubscribe),

    path('changeInfo', user_info.update_user_info),
    path('userUploadResume', user_info.upload_resume),
    path('getUserInfo', user_info.get_user_info),
    path('getUserInfoById', user_info.get_user_info_by_id),

    path('getRecommendRecruit', recommend.get_recommend_recruit),
    path('getRecommendUser', recommend.get_recommend_user),

    path('searchUser', search.search_user),

    path('optimize_resume', others.optimize_resume),
]