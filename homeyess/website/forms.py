"""
homeyess/website/forms.py
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
<<<<<<< HEAD
from django.forms import ModelForm
from django.db import models
from .models import RideRequestPost
from django.urls import reverse
=======
from website.models import JobPost
>>>>>>> aee87a54ec4434ea8ef992c8562c52c40588857a

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=False, help_text='Optional')
    phone = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='###-###-####. Optional')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone')
<<<<<<< HEAD
        
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
    
'''
class JobForm(forms.ModelForm):
    location = forms.CharField(max_length=100, required=True)
    wage = forms.CharField(max_length=100, required=True)
    hours = forms.CharField(max_length=100, required=True)
=======

class JobForm(forms.ModelForm):
    location = forms.CharField(max_length=100, required=True)
    wage = forms.CharField(max_length=100, required=True) #forms.DecimalField(max_digits=6, decimal_places=2, min_value=0.0, required=True)
    hours = forms.CharField(max_length=100, required=True) #forms.IntegerField(min_value=0, required=True)
>>>>>>> aee87a54ec4434ea8ef992c8562c52c40588857a
    job_title = forms.CharField(max_length=100, required=True)
    short_summary = forms.CharField(max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = JobPost
<<<<<<< HEAD
        fields = ('location', 'wage', 'hours', 'job_title', 'short_summary', 'description')
'''
=======
        fields = ('location', 'wage', 'hours', 'job_title', 'short_summary', 'description')
>>>>>>> aee87a54ec4434ea8ef992c8562c52c40588857a
