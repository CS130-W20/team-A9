"""
homeyess/website/forms.py
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from website.models import Profile

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, required=False, help_text='Optional')
    phone = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='###-###-####. Optional')
    user_type = forms.ChoiceField(choices=[(tag.value, tag.name) for tag in Profile.UserType], initial=Profile.UserType.Homeless)
    car_plate = forms.CharField(max_length=8, required=False)
    car_make = forms.CharField(max_length=20, required=False)
    car_model = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        car_make = cleaned_data.get("car_make")
        car_model = cleaned_data.get("car_model")
        car_plate = cleaned_data.get("car_plate")
        if user_type == 'V' and (car_make == '' or car_make == None or car_model == None or car_plate == None or car_model == '' or car_plate == ''):
            raise forms.ValidationError("Volunteers must fill out car information")
        
    
