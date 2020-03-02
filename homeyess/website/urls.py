"""
homeyess/website/urls.py
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup/<str:user_type>/', views.signup, name='signup'),
    path('accounts/user-type', views.user_type, name='user_type'),
    path('dashboard/<str:user_id>/', views.dashboard, name='dashboard'),
    path('view-ride/<int:ride_id>/', views.viewrideform, name='view_ride'),
    path('update-ride/<int:ride_id>', views.RequestRideEdit.as_view(), name='update_ride'),
    path('request-ride', views.RequestRideCreate.as_view(), name='request_ride'),
    path('delete-ride/<int:ride_id>/', views.DeleteRideRequest, name='delete_ride'),
    path('jobs/', views.postjob, name='post_job'),
    path('jobs/<int:job_id>/', views.editjob, name='edit_job'),
    path('search_rides', views.ride_board, name='search_rides'),
    path('confirm_ride/<int:ride_id>', views.confirmRide, name='confirm_ride'),
    path('job-board/', views.job_board, name="job_board"),
    path('job-detail/<int:job_id>/', views.job_detail, name="job_detail"),
]
