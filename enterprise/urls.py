from django.urls import path
from . import views

urlpatterns = [
    path('createEnterprise/', views.createEnterprise),
    path('addEmployee/', views.addEmployee),
    path('updateEnterpriseInfo/', views.updateEnterpriseInfo),
    path('joinEnterprise/', views.joinEnterprise),
    path('completeEnterpriseInfo/', views.completeEnterpriseInfo),
    path('exitEnterprise/', views.exitEnterprise),
    path('expelEmployee/', views.expelEmployee),
    path('searchEnterprise/', views.searchEnterprise),
    path('getEnterpriseInfo/', views.getEnterpriseInfo),
    path('postRecruitment/', views.postRecruitment),
    path('getRecruitment/', views.getRecruitment),
    path('getPostRecruitment/', views.getPostRecruitment),
    path('sendResume/', views.sendResume),
    path('getCandidates/', views.getCandidates),
    path('getResume/', views.getResume),
    path('searchPost/', views.searchPost),
]
