"""
homeyess/website/forms.py
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from website.models import Profile, JobPost
from django.forms import ModelForm, Form
from django.db import models
from .models import Ride
from django.urls import reverse

class SignUpForm(UserCreationForm):
    '''SignUpForm for users, companies, and volunteers

    '''

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.user_type = user_type

        if user_type == 'C':
            self.fields['first_name'] = forms.CharField(max_length=30, required=True, help_text="Required.", label="Name")
        else:
            self.fields['first_name'] = forms.CharField(max_length=30, required=True, help_text="Required.", label="First Name")
        if user_type != 'C':
            self.fields['last_name'] = forms.CharField(max_length=30, required=False, help_text="Companies need not fill this out.")
        self.fields['email'] = forms.EmailField(max_length=254, required=False, help_text='Optional.')
        self.fields['phone'] = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='Optional.', label="Phone Number (###-###-####)")
        if user_type == 'V':
            self.fields['car_plate'] = forms.CharField(max_length=8, required=False, label="License Plate Number", help_text="Required for volunteers.")
            self.fields['car_make'] = forms.CharField(max_length=20, required=False, label="Make of Car", help_text="Required for volunteers.")
            self.fields['car_model'] = forms.CharField(max_length=20, required=False, label="Model of Car", help_text="Required for volunteers.")
        if user_type != 'C':
            self.fields['home_address'] = forms.CharField(max_length=200, required=False, label="Home Address", help_text="Companies need not fill this out.")


    class Meta:
        model = User
        fields = fields = ('first_name', 'email', 'username', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        user_type = self.user_type
        car_make = cleaned_data.get("car_make", None)
        car_model = cleaned_data.get("car_model", None)
        car_plate = cleaned_data.get("car_plate", None)
        last_name = cleaned_data.get("last_name", None)
        home_address = cleaned_data.get("home_address", None)
        if user_type == 'V' and (car_make == '' or car_make == None or car_model == None or car_plate == None or car_model == '' or car_plate == ''):
            raise forms.ValidationError("Car information is required.")
        if user_type != 'C' and (last_name == '' or last_name == None):
            raise forms.ValidationError("First and last names are required")
        if user_type != 'C' and (home_address == '' or home_address == None):
            raise forms.ValidationError("Home address is required")

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
    '''Ride Request Form for people experiencing homelessness to request a ride to their interview
    '''
    class Meta:
        model = Ride
        fields = ['interview_datetime', 'interview_duration', 'interview_address', 'interview_company']

    class DateInput(forms.DateInput):
        input_type = 'date'
    interview_datetime = forms.DateTimeField(required=True, widget=forms.DateTimeInput, help_text='Format YYYY-MM-DD HH:MM:SS')
    interview_duration = forms.IntegerField(required=True, help_text='(in minutes)')
    interview_address = forms.CharField(max_length=200, required=True)
    interview_company = forms.CharField(max_length=100, required=True)


class FilterForm(Form):
    start_datetime = forms.DateTimeField(required=False)
    end_datetime = forms.DateTimeField(required=False)
    max_range = forms.IntegerField(required=False)

class UserTypeForm(Form):
    user_type = forms.ChoiceField(choices=[(tag.value, tag.name) for tag in Profile.UserType], required=True)
