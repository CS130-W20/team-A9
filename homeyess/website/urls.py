from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup', views.signup, name='signup'),
    path('dashboard/<str:user_id>/', views.dashboard, name='dashboard'),
    path('request-ride', views.request_ride, name='request_ride'),
]
