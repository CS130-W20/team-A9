"""
homeyess/website/urls.py
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup', views.signup, name='signup'),
    path('dashboard/<str:user_id>/', views.dashboard, name='dashboard'),
<<<<<<< HEAD
    path('request-ride', views.RequestRideCreate.as_view(), name='request_ride'),
    path('jobs/<str:pk>/post_job', views.PostJob.as_view(), name='postjob'),
    path('jobs/<str:user_id>/<int:pk>/edit_job', views.EditJob.as_view(), name='editjob'),
]
=======
    path('dashboard/<str:user_id>/', views.post_job, name='post_job'),
    path('dashboard/<str:user_id>/<int:job_id>', views.edit_job, name='edit_job'),
]
>>>>>>> aee87a54ec4434ea8ef992c8562c52c40588857a
