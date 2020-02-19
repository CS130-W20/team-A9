from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from website.models import JobPost

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=False, help_text='Optional')
    phone = forms.RegexField(regex='\d{3}-\d{3}-\d{4}', required=False, help_text='###-###-####. Optional')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone')

class JobForm(forms.ModelForm):
    location = forms.CharField(max_length=100, required=True)
    wage = forms.CharField(max_length=100, required=True) #forms.DecimalField(max_digits=6, decimal_places=2, min_value=0.0, required=True)
    hours = forms.CharField(max_length=100, required=True) #forms.IntegerField(min_value=0, required=True)
    job_title = forms.CharField(max_length=100, required=True)
    short_summary = forms.CharField(max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = JobPost
        fields = ('location', 'wage', 'hours', 'job_title', 'short_summary', 'description')