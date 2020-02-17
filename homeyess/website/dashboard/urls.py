from django.urls import path

from . import views

urlpatterns = [
    path('homeless/<?username>', views.homeless, name='homeless'),
    path('company/<?username>', views.homeless, name='company'),
    path('volunteer/<?username>', views.homeless, name='volunteer'),
]
