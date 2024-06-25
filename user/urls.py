from django.urls import path
from views import account, user_info, recommend, search, others

urlpatterns = [
    path('register/', account.register),
    path('login/', account.login),
    path('active_user/', account.active_user),
    path('unsubscribe/', account.unsubscribe),

    path('changeInfo/', user_info.update_user_info),
    path('upload_user_avatar/', user_info.upload_user_avatar),
    path('userUploadResume/', user_info.upload_resume),
    path('getUserInfo/', user_info.get_user_info),
    path('get_certain_user_info/', user_info.get_certain_user_info),
    path('userDownloadResume/', user_info.user_download_resume),

    path('get_recruit_info/', recommend.get_recruit_info),
    path('get_similar_enterprise/', recommend.get_similar_enterprise),
    path('get_similar_user/', recommend.get_similar_user),

    path('search_user/', search.search_user),

    path('optimize_resume/', others.optimize_resume),
]