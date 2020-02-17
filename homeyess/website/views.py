from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from website.forms import SignUpForm, JobPostForm

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.phone = form.cleaned_data.get('phone')
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

def jobpost(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            # TODO: save to the database
            return redirect('/')
    else:
        form = JobPostForm()

    return render(request, 'registration/jobpost.html', {'form': form})

