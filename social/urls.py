from django.urls import path

from . import views

urlpatterns = [
    path('publish_activity/', views.publish_activity),
    path('update_activity/', views.update_activity),
    path('delete_activity/', views.delete_activity),
    path('forward_activity/', views.forward_activity),
    path('display_activity/', views.display_activity),
    path('get_user_activity_list/', views.get_user_activity_list),
    path('get_enter_activity_list/', views.get_enter_activity_list),
]
