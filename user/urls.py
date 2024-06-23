from django.urls import path
from . import views

urlpatterns = [
    path('register/', register),
    path('login/', login),
]