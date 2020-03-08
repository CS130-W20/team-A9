"""
homeyess/website/forms.py
"""
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Form

from .fields import *
from .models import Profile, JobPost, Ride


class SignUpForm(UserCreationForm):
    """SignUpForm for users, companies, and volunteers
    """

    def __init__(self, *args, **kwargs):
        """initializes the form
        :param kwargs["user_type"]: the type of the user ("V", "H", "C")
        :type kwargs["user_type"]: string
        """
        user_type = kwargs.pop("user_type", None)
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.user_type = user_type
        field_order = []

        if user_type == "C":
            self.fields["first_name"] = BootstrapCharField(max_length=30, required=True, label="Company Name")
        else:
            self.fields["first_name"] = BootstrapCharField(max_length=30, required=True, label="First Name")
        field_order.append("first_name")
        if user_type != "C":
            self.fields["last_name"] = BootstrapCharField(max_length=30, required=False)
            field_order.append("last_name")
        self.fields["username"] = BootstrapCharField(required=True)
        field_order.append("username")
        self.fields["password1"] = BootstrapCharField(required=True, widget=forms.PasswordInput(attrs={"class": FORM_CLASS}), label="Password")
        field_order.append("password1")
        self.fields["password2"] = BootstrapCharField(required=True, widget=forms.PasswordInput(attrs={"class": FORM_CLASS}), label="Confirm password")
        field_order.append("password2")
        self.fields["email"] = BootstrapEmailField(max_length=254, required=False, help_text="Optional.")
        field_order.append("email")
        self.fields["phone"] = BootstrapRegexField(regex="\d{10}", required=False, help_text="Optional.", label="Phone Number (##########)", error_messages={"invalid": "Incorrect phone number format"})
        field_order.append("phone")
        if user_type == "V":
            self.fields["car_plate"] = BootstrapCharField(max_length=8, required=False, label="License Plate Number")
            self.fields["car_make"] = BootstrapCharField(max_length=20, required=False, label="Make of Car")
            self.fields["car_model"] = BootstrapCharField(max_length=20, required=False, label="Model of Car")
            field_order.append("car_plate")
            field_order.append("car_make")
            field_order.append("car_model")
        if user_type == "V":
            self.fields["home_address"] = BootstrapCharField(max_length=200, required=False, label="Home Address")
            field_order.append("home_address")
        if user_type == "H":
            self.fields["home_address"] = BootstrapCharField(max_length=200, required=False, label="Pickup Address")
            field_order.append("home_address")

        self.order_fields(field_order)

    class Meta:
        model = User
        fields = ("first_name", "email", "username", "password1", "password2")

    def clean(self):
        """checks that signups meet proper constraints such as volunteer must have car
        """
        cleaned_data = super().clean()
        user_type = self.user_type
        car_make = cleaned_data.get("car_make", None)
        car_model = cleaned_data.get("car_model", None)
        car_plate = cleaned_data.get("car_plate", None)
        last_name = cleaned_data.get("last_name", None)
        home_address = cleaned_data.get("home_address", None)
        if user_type == "V" and (car_make == "" or car_make == None or car_model == None or car_plate == None or car_model == "" or car_plate == ""):
            raise forms.ValidationError("Car information is required.")
        if user_type != "C" and (last_name == "" or last_name == None):
            raise forms.ValidationError("First and last names are required")
        if user_type != "C" and (home_address == "" or home_address == None):
            raise forms.ValidationError("Home address is required")

class PostJobForm(ModelForm):
    """PostJobForm for companies to post and edit jobs
    """

    location = BootstrapCharField(max_length=100, required=True, help_text="Location of job itself, not interview.")
    wage = BootstrapCharField(max_length=100, required=True)
    hours = BootstrapCharField(max_length=100, required=True, help_text="Number of hours per day / week, expected work hours, etc.")
    job_title = BootstrapCharField(max_length=100, required=True)
    short_summary = BootstrapCharField(max_length=200, required=True, help_text="First description seen by potential applicants.")
    description = BootstrapCharField(widget=forms.Textarea(attrs={"rows": "5", "class": FORM_CLASS}), required=True, help_text="Detail job responsibilities and roles, desired skills and experiences, and means of getting into contact with you.")

    class Meta:
        model = JobPost
        fields = ["location", "wage", "hours", "job_title", "short_summary", "description"]

class RideRequestForm(ModelForm):
    """Ride Request Form for people experiencing homelessness to request a ride to their interview
    """
    class Meta:
        model = Ride
        fields = ["interview_datetime", "interview_duration", "interview_address", "interview_company"]

    interview_datetime = BootstrapDateTimeField(required=True, help_text="e.g. 2020-09-22 14:00", label="Interview Date and Time")
    interview_duration = BootstrapIntegerField(required=True, help_text="(in minutes)")
    interview_address = BootstrapCharField(max_length=200, required=True)
    interview_company = BootstrapCharField(max_length=100, required=True)

class JobBoardFilterForm(Form):
    """Form to allow homeless people to filter job results
    """
    location = BootstrapCharField(required=False)
    job_title = BootstrapCharField(required=False)

class RideSearchFilterForm(Form):
    """Form to allow volunteers to filter ride requests
    """
    start_datetime = BootstrapDateTimeField(required=False, widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': '2020-09-22 14:00'}))
    end_datetime = BootstrapDateTimeField(required=False, widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2020-09-22 20:00'}))
    max_distance = BootstrapIntegerField(required=False)

class UserTypeForm(Form):
    """Form to allow users to select the type of user they are in order to be directed to the relevant signup form
    """
    user_type = forms.ChoiceField(choices=[(tag.value, tag.name) for tag in Profile.UserType], required=True, widget=forms.RadioSelect(), initial="H")
