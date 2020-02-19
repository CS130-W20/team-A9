from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup', views.signup, name='signup'),
    path('dashboard/<str:user_id>/', views.dashboard, name='dashboard'),
    path('dashboard/<str:user_id>/', views.post_job, name='post_job'),
    path('dashboard/<str:user_id>/<int:job_id>', views.edit_job, name='edit_job'),
]