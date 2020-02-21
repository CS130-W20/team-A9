"""
homeyess/website/forms.py
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from website.models import Profile, JobPost
from django.forms import ModelForm
from django.db import models
from .models import RideRequestPost
from django.urls import reverse

class SignUpForm(UserCreationForm):
    '''SignUpForm for users, companies, and volunteers
    '''
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.", label="First Name / Company Name")
    last_name = forms.CharField(max_length=30, required=False, help_text="Companies need not fill this out.")
    email = forms.EmailField(max_length=254, required=False, help_text='Optional.')
    phone = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='Optional.', label="Phone Number (###-###-####)")
    user_type = forms.ChoiceField(choices=[(tag.value, tag.name) for tag in Profile.UserType], initial=Profile.UserType.Homeless)
    car_plate = forms.CharField(max_length=8, required=False, label="License Plate Number", help_text="Required for volunteers.")
    car_make = forms.CharField(max_length=20, required=False, label="Make of Car", help_text="Required for volunteers.")
    car_model = forms.CharField(max_length=20, required=False, label="Model of Car", help_text="Required for volunteers.")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'username', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        car_make = cleaned_data.get("car_make")
        car_model = cleaned_data.get("car_model")
        car_plate = cleaned_data.get("car_plate")
        if user_type == 'V' and (car_make == '' or car_make == None or car_model == None or car_plate == None or car_model == '' or car_plate == ''):
            raise forms.ValidationError("Volunteers must fill out car information")
        
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
    
class PostJobForm(ModelForm):
    '''PostJobForm for companies to post and edit jobs
    '''
    location = forms.CharField(max_length=100, required=True, help_text='Location of job itself, not interview.')
    wage = forms.CharField(max_length=100, required=True)
    hours = forms.CharField(max_length=100, required=True)
    job_title = forms.CharField(max_length=100, required=True)
    short_summary = forms.CharField(max_length=200, required=True, help_text='First description seen by potential applicants.')
    description = forms.CharField(widget=forms.Textarea, required=True, help_text='Detail job responsibilities and roles, desired skills and experiences, and means of getting into contact with you.')

    class Meta:
        model = JobPost
        fields = ['location', 'wage', 'hours', 'job_title', 'short_summary', 'description']

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
    
