from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.db import models

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=False, help_text='Optional')
    phone = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='###-###-####. Optional')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone')

class RideRequestForm():
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=False, help_text='Optional')
    phone = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='###-###-####. Optional')
    interview_datetime = forms.CharField(max_length=30, required=True)
    interview_duration = forms.CharField(max_length=30, required=True)
    pickup_address = models.CharField(max_length=200)
    pickup_datetime = models.DateTimeField()
    interview_address = models.CharField(max_length=200)
    interview_company = models.CharField(max_length=100)
    end_datetime = models.DateTimeField()

