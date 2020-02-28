'''
homeyess/website/views.py
'''
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Ride, JobPost, RideRequestPost
from django.views.generic.edit import CreateView, UpdateView, ListView

from website.forms import SignUpForm, RideRequestForm, PostJobForm
from .models import Profile, Ride, JobPost, RideRequestPost
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
import requests
from homeyess.settings import GOOGLE_MAPS_API_KEY
import functools

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
    '''Renders the dashboard page for all users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the homeless.html, company.html, or volunteer.html template which matches the type of the requesting user
    :rtype: HttpResponse
    '''
    user = User.objects.get(pk=user_id)
    if user.profile.user_type == 'V':
        return volunteer(request, user)
    elif user.profile.user_type == 'H':
        return homeless(request, user)
    elif user.profile.user_type == 'C':
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
    unconfirmed_rides = Ride.objects.filter(homeless = user.profile, volunteer = None, interview_datetime__gt = timezone.now())
    confirmed_rides = Ride.objects.filter(homeless = user.profile, interview_datetime__gt = timezone.now()).exclude(volunteer = None)
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
    job_posts = JobPost.objects.filter(company=user.profile)
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
    confirmed_rides = Ride.objects.filter(volunteer = user.profile, interview_datetime__gt = timezone.now())
    finished_rides = Ride.objects.filter(volunteer = user.profile, interview_datetime__lte = timezone.now())
    context = {'user': user, 'confirmed_rides': confirmed_rides, 'finished_rides': finished_rides}
    return render(request, 'dashboard/volunteer.html', context)

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

def ViewRideForm(request, post_id):
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
		id_ = self.kwargs.get('post_id')
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

def map(request):
    return render(request, 'map.html')

class RideRequestView(ListView):
    model = Ride
    template_name = 'map.html'

    def get_queryset(self):
        pass

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = FilterForm(initial={
            'date': self.request.GET.get('date', ''),
            'start_time': self.request.GET.get('start_time', ''),
            'end_time': self.request.GET.get('end_time', ''),
            'max_range': self.request.GET.get('max_range', ''),
            'start_address': self.request.GET.get('start_address'),
        })
        return context

def distanceTimeVector(v_start, hp_start, interview_location, interview_duration):
    URL = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    PARAMS = {
        'key': GOOGLE_MAPS_API_KEY,
        'origins': v_start + '|' + hp_start + '|' + interview_location,
        'destinations': v_start + '|' + hp_start + '|' + interview_location,
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()

    if data['status'] != 'OK':
        return None

    # we need:
    # v_start -> hp_start (0, 1)
    # hp_start -> interview_location (1, 2)
    # interview_location -> hp_start (2, 1)
    # hp_start -> v_start (1, 0)

    INDICES = [(0, 1), (1, 2), (2, 1), (1, 0)]
    time_distance_vector = []
    for index0, index1 in INDICES:
        if data['rows'][index0]['elements'][index1]['status'] != 'OK':
            return None
        distance_in_meters = data['rows'][index0]['elements'][index1]['distance']['value']
        time_in_seconds = data['rows'][index0]['elements'][index1]['duration']['value']

        distance_in_miles = 0.000621371 * distance_in_meters
        time_in_minutes = time_in_seconds / 60

        time_distance_vector.append((time_in_seconds, distance_in_miles))

    # insert the interview in between the driving
    time_distance_vector.insert(2, (interview_duration, 0))
    return time_distance_vector
