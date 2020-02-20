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
    path('jobs/<str:pk>/post_job', views.PostJob.as_view(), name='postjob'),
    path('jobs/<str:user_id>/<int:pk>/edit_job', views.EditJob.as_view(), name='editjob'),
]
