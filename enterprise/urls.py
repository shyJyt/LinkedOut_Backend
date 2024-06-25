from django.urls import path
from .views.employee.enterprise import joinEnterprise, completeEnterpriseInfo, createEnterprise, exitEnterprise
from .views.employee.recruitment import sendResume
from .views.manager.manage_employee import addEmployee, expelEmployee
from .views.manager.manage_enterprise_info import updateEnterpriseInfo
from .views.manager.manage_recruitment import postRecruitment, getCandidates, getResume, hire
from .views.search.enterprise import searchEnterprise, getEnterpriseInfo
from .views.search.recruitment import getRecruitment, getPostRecruitment, searchPost

urlpatterns = [
    path('createEnterprise/', createEnterprise),
    path('addEmployee/', addEmployee),
    path('updateEnterpriseInfo/', updateEnterpriseInfo),
    path('joinEnterprise/', joinEnterprise),
    path('completeEnterpriseInfo/', completeEnterpriseInfo),
    path('exitEnterprise/', exitEnterprise),
    path('expelEmployee/', expelEmployee),
    path('searchEnterprise/', searchEnterprise),
    path('getEnterpriseInfo/', getEnterpriseInfo),
    path('postRecruitment/', postRecruitment),
    path('getRecruitment/', getRecruitment),
    path('getPostRecruitment/', getPostRecruitment),
    path('sendResume/', sendResume),
    path('getCandidates/', getCandidates),
    path('getResume/', getResume),
    path('searchPost/', searchPost),
    path('hire/', hire),
]
