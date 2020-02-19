from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from website.forms import SignUpForm, RideRequestForm
from .models import Profile, Ride, JobPost
import datetime

def index(request):
    return render(request, 'index.html')

def signup(request):
    print(request.method)
    if request.method == 'POST':
        print(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("Hello")
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

def dashboard(request, user_id):
    user = Profile.objects.get(pk=user_id)
    if user.user_type == "V":
        return volunteer(request, user)
    elif user.user_type == "H":
        return homeless(request, user)
    elif user.user_type == "C":
        return company(request, user)

def homeless(request, user):
    unconfirmed_rides = Ride.objects.filter(homeless = user, volunteer = None, interview_datetime__gt = datetime.datetime.now())
    confirmed_rides = Ride.objects.filter(homeless = user, interview_datetime__gt = datetime.datetime.now()).exclude(volunteer = None)
    context = {'user': user, 'unconfirmed_rides': unconfirmed_rides, 'confirmed_rides': confirmed_rides}
    return render(request, 'dashboard/homeless.html', context)

def company(request, user):
    job_posts = JobPost.objects.filter(company=user)
    context = {'user': user, 'job_posts': job_posts}
    return render(request, 'dashboard/company.html', context)

def volunteer(request, user):
    confirmed_rides = Ride.objects.filter(volunteer = user, interview_datetime__gt = datetime.datetime.now())
    finished_rides = Ride.objects.filter(volunteer = user, interview_datetime__lte = datetime.datetime.now())
    context = {'user': user, 'confirmed_rides': confirmed_rides, 'finished_rides': finished_rides}
    return render(request, 'dashboard/volunteer.html', context)

def request_ride(request):
    if request.method == 'POST':
        print(request.POST)
        form = RideRequestForm(request.POST)
        if form.is_valid():
            return redirect('/')
    else:
        form = RideRequestForm()
        print(form)
    return render(request, 'ride_request/request_ride.html', {'form': form})

