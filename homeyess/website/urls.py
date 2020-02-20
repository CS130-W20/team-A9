"""
homeyess/website/urls.py
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup', views.signup, name='signup'),
    path('dashboard/<str:user_id>/', views.dashboard, name='dashboard'),
    path('request-ride', views.RequestRideCreate.as_view(), name='request_ride'),
    path('jobs/<str:user_id>/', views.postjob, name='postjob'),
    path('jobs/<str:user_id>/<int:job_id>/', views.editjob, name='editjob')
]
