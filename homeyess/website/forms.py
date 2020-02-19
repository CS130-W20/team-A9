from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.db import models
from .models import RideRequestPost
from django.urls import reverse

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=False, help_text='Optional')
    phone = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='###-###-####. Optional')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone')

class RideRequestForm(ModelForm):
    class Meta:
        model = RideRequestPost
        fields = ['first_name', 'last_name', 'email', 'pickup_date', 'interview_duration', 'pickup_address', 'interview_address']

    class DateInput(forms.DateInput):
        input_type = 'date'
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=False, help_text='Optional')
    pickup_date = forms.DateField(widget=DateInput, required=True)
    interview_duration = forms.CharField(max_length=30, required=True)
    pickup_address = forms.CharField(max_length=200, required=True)
    interview_address = forms.CharField(max_length=200, required=True)
    
