"""
homeyess/website/urls.py
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup', views.signup, name='signup'),
    path('dashboard/<str:user_id>/', views.dashboard, name='dashboard'),
    path('ViewRideForm/<int:post_id>', views.viewrideform, name='viewrideform'),
    path('ViewRideForm/<int:post_id>/Update', views.RequestRideEdit.as_view(), name='update_ride'),
    path('request-ride', views.RequestRideCreate.as_view(), name='request_ride'),
    path('jobs/<str:user_id>/', views.postjob, name='post_job'),
    path('jobs/<str:user_id>/<int:job_id>/', views.editjob, name='edit_job'),
    path('jobs/delete/<str:user_id>/<int:job_id>/', views.deletejob, name='delete_job'),
    path('search_rides', views.RideRequestListView.as_view(), name='search_rides'),
    path('confirm_ride/<int:ride_id>', views.confirmRide, name='confirm_ride'),
    path('job-board/', views.job_board, name="job_board"),
    path('job-detail/<int:job_id>/', views.job_detail, name="job_detail"),
]
