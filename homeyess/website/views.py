"""
homeyess/website/views.py
"""
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Ride, JobPost, RideRequestPost
from django.views.generic.edit import CreateView, UpdateView

from website.forms import SignUpForm, RideRequestForm, PostJobForm
from .models import Profile, Ride, JobPost, RideRequestPost
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .decorators import is_homeless, is_volunteer, is_company
from django.conf import settings

import math

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
            user.profile.home_address = form.cleaned_data.get('home_address')
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
    '''Renders the dashboard page for all users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the homeless.html, company.html, or volunteer.html template which matches the type of the requesting user
    :rtype: HttpResponse
    '''
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return HttpResponse(status=404)

    if user.profile.user_type == "V":
        return volunteer(request, user)
    elif user.profile.user_type == "H":
        return homeless(request, user)
    elif user.profile.user_type == "C":
        return company(request, user)
    return HttpResponse(status=404)

def homeless(request, user):
    '''Renders the dashboard page for homeless users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the homeless.html template
    :rtype: HttpResponse
    '''
    unconfirmed_rides = Ride.objects.filter(homeless = user.profile, volunteer = None, interview_datetime__gt = timezone.now()).order_by('-interview_datetime')
    confirmed_rides = Ride.objects.filter(homeless = user.profile, interview_datetime__gt = timezone.now()).exclude(volunteer = None).order_by('-interview_datetime')
    context = {'user': user, 'unconfirmed_rides': unconfirmed_rides, 'confirmed_rides': confirmed_rides}
    return render(request, 'dashboard/homeless.html', context)

def company(request, user):
    '''Renders the dashboard page for company users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the company.html template
    :rtype: HttpResponse
    '''
    job_posts = JobPost.objects.filter(company=user.profile).order_by('-created')
    context = {'user': user, 'job_posts': job_posts}
    return render(request, 'dashboard/company.html', context)

def volunteer(request, user):
    '''Renders the dashboard page for volunteer users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the volunteer.html template
    :rtype: HttpResponse
    '''
    confirmed_rides = Ride.objects.filter(volunteer = user.profile, interview_datetime__gt = timezone.now()).order_by('-interview_datetime')
    finished_rides = Ride.objects.filter(volunteer = user.profile, interview_datetime__lte = timezone.now()).order_by('-interview_datetime')
    total_time = 0
    for ride in finished_rides:
        time = ride.end_datetime - ride.pickup_datetime
        hours = time.seconds/60/60
        total_time+=hours

    total_time = math.floor(total_time)
    context = {'user': user, 'confirmed_rides': confirmed_rides, 'finished_rides': finished_rides, 'total_time': total_time}
    return render(request, 'dashboard/volunteer.html', context)

@method_decorator(user_passes_test(is_homeless, login_url='accounts/login/'), name='dispatch')
def job_board(request):
    '''Renders the job board page for homeless users to view jobs

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :return: the rendered job board page using the job_board.html template 
    :rtype: HttpResponse
    '''
    job_posts = JobPost.objects.all().order_by('-created')
    return render(request, 'job_board/job_board.html', {'job_posts': job_posts})

def job_detail(request, job_id):
    '''Renders the job detail page to see more information on a job from the job board

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the job to be viewed
    :type request: String
    :return: the rendered job detail page using the job_detail.html template 
    :rtype: HttpResponse
    '''
    job = JobPost.objects.filter(pk=job_id).first()
    if not job:
        return HttpResponse(status=404)
    return render(request, 'job_board/job_detail.html', {'job': job})

def map(request):
    GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY
    return render(request, 'map.html', {'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY})

class RequestRideCreate(CreateView):
	'''Object used to render the ride request creation view

	:param template_name: the name of the template used to render the view
	:type template_name: string
	:param form_class: the form that specifies what data needs to be input
	:type form_class: ModelFormMetaclass
	:param queryset: the queryable attributes of the form
	:type queryset: QuerySet
	'''
	template_name = 'ride_request/request_ride.html'
	form_class = RideRequestForm
	queryset = RideRequestPost.objects.all()


def viewrideform(request, post_id):
	'''Renders the view that allows people experiencing homelessness to view a specific ride request
	he/she filled out, so that they can review and potentially edit the form

	:param request: The http request containing user information or extra arguments
	:type request: HttpRequest
	:param post_id: The ride request post's idea
	:type post_id: int
	'''
	form_set = RideRequestPost.objects.filter(id=post_id)
	form = form_set[0]
	context = {'form': form}
	return render(request, 'ride_request/ViewRideForm.html', context)

class RequestRideEdit(UpdateView):
	'''Object used to render the request form's update view

	:param template_name: the name of the template used to render the view
	:type template_name: string
	:param form_class: the form that specifies what data needs to be input
	:type form_class: ModelFormMetaclass
	:param queryset: the queryable attributes of the form
	:type queryset: QuerySet
	'''
	template_name = 'ride_request/request_ride.html'
	form_class = RideRequestForm
	queryset = RideRequestPost.objects.all()

	def get_object(self):
		id_ = self.kwargs.get("post_id")
		return get_object_or_404(RideRequestPost, id=id_)

def editjob(request, user_id, job_id):
    '''Renders the editjob form on GET; processes the editjob form on POST

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The primary key used to index the user that owns the job
    :type request: string
    :param job_d: The primary key used to index the specific job we are editing
    :type request: int
    :return: the rendered JobForm or a redirect to the company's dashboard
    :rtype: HttpResponse
    '''
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
    '''Renders the postjob form on GET; processes the postjob form on POST

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The primary key used to index the user that owns the job
    :type request: string
    :return: the rendered JobForm or a redirect to the company's dashboard
    :rtype: HttpResponse
    '''
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
