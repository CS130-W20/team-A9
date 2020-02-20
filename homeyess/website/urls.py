from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup', views.signup, name='signup'),
    path('dashboard/<str:user_id>/', views.dashboard, name='dashboard'),
    path('request-ride/', views.RequestRideCreate.as_view(), name='request_ride'),
    path('ViewRideForm/<int:post_id>', views.ViewRideForm, name='ViewRideForm'),
    path('ViewRideForm/<int:post_id>/Update', views.RequestRideEdit.as_view(), name='update_ride'),
]
