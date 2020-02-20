"""
homeyess/website/views.py
"""
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from website.forms import SignUpForm, RideRequestForm, PostJobForm
from .models import Profile, Ride, JobPost, RideRequestPost
from django.views.generic.edit import CreateView
import datetime

def index(request):
    '''Renders the index / home page

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :return: the rendered index page using the index.html template
    :rtype: HttpResponse
    '''
    return render(request, 'index.html')

def signup(request):
    '''Renders the signup form on GET; processes the signup form on POST

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :return: the rendered SignUpForm or a redirect to homepage
    :rtype: HttpResponse
    '''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.user_type = form.cleaned_data.get('user_type')
            user.profile.car_plate = form.cleaned_data.get('car_plate')
            user.profile.car_make = form.cleaned_data.get('car_make')
            user.profile.car_model = form.cleaned_data.get('car_model')
            user.profile.total_volunteer_minutes = 0
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
  
class RequestRideCreate(CreateView):
    template_name = 'ride_request/request_ride.html'
    form_class = RideRequestForm
    queryset = RideRequestPost.objects.all()

def editjob(request, user_id, job_id):
    job_post = JobPost.objects.get(pk=job_id)
    if request.method == 'POST':
        form = PostJobForm(request.POST, instance=job_post)
        if form.is_valid():
            form.save()
            user = Profile.objects.get(pk=user_id)
            job_posts = JobPost.objects.filter(company=user)
            context = {'user': user, 'job_posts': job_posts}
            return render(request, 'dashboard/company.html', context)
    else:
        form = PostJobForm(instance=job_post)

    return render(request, 'jobs/editjob.html', {'form': form})

def postjob(request, user_id):
    if request.method == 'POST':
        form = PostJobForm(request.POST)
        if form.is_valid():
            user = Profile.objects.get(pk=user_id)
            job_post = JobPost(company=user, **form.cleaned_data)
            job_post.save()
            job_posts = JobPost.objects.filter(company=user)
            context = {'user': user, 'job_posts': job_posts}
            return render(request, 'dashboard/company.html', context)
    else:
        form = PostJobForm(initial={'wage': '15.50 usd/hr', 'hours': '40 hr/wk'})

    return render(request, 'jobs/postjob.html', {'form': form})