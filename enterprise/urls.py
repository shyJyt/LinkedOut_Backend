from django.urls import path
from .views.employee.enterprise import (join_enterprise, complete_enterprise_info,
                                        create_enterprise, exit_enterprise, get_ee_info)
from .views.employee.recruitment import send_resume, accept_hire
from .views.manager.manage_employee import add_employee, expel_employee
from .views.manager.manage_enterprise_info import update_enterprise_info
from .views.manager.manage_recruitment import post_recruitment, get_candidates, get_resume, hire
from .views.search.enterprise import search_enterprise, get_enterprise_info
from .views.search.recruitment import get_recruitment, get_post_recruitment, search_post, search_post_by_name

urlpatterns = [
    path('createEnterprise/', create_enterprise),
    path('addEmployee/', add_employee),
    path('updateEnterpriseInfo/', update_enterprise_info),
    path('joinEnterprise/', join_enterprise),
    path('completeEnterpriseInfo/', complete_enterprise_info),
    path('exitEnterprise/', exit_enterprise),
    path('expelEmployee/', expel_employee),
    path('searchEnterprise/', search_enterprise),
    path('getEnterpriseInfo/', get_enterprise_info),
    path('postRecruitment/', post_recruitment),
    path('getRecruitment/', get_recruitment),
    path('getPostRecruitment/', get_post_recruitment),
    path('sendResume/', send_resume),
    path('getCandidates/', get_candidates),
    path('getResume/', get_resume),
    path('searchPost/', search_post),
    path('hire/', hire),
    path('acceptHire/', accept_hire),
    path('getEEInfo/', get_ee_info),
    path('searche_post_by_name/', search_post_by_name)
]
