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

class JobPostForm(forms.ModelForm):
    company = forms.CharField(max_length=30, required=True)
    location = forms.CharField(max_length=100, required=True)
    wage = forms.DecimalField(max_digits=8, decimal_places=2, required=True)
    hours = forms.IntegerField(min_value=0, max_value=200, required=True)
    job_title = forms.CharField(max_length=100, required=True)
    short_summary = forms.CharField(max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))
    I_agree_to_the_terms_and_servies = forms.BooleanField(required = True)

    class Meta:
        model = JobPost
        fields = ('company', 'location', 'wage', 'hours', 'job_title', 'short_summary', 'description')
