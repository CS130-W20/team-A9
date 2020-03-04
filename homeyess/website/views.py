'''
homeyess/website/views.py
'''
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Ride, JobPost
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from .forms import SignUpForm, RideRequestForm, PostJobForm, FilterForm, UserTypeForm, JobBoardFilterForm
from website import job_utils
from .models import Profile, Ride, JobPost
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from .decorators import is_homeless, is_volunteer, is_company
import requests
from homeyess.settings import GOOGLE_MAPS_API_KEY
from django.conf import settings
import math
from django.core.serializers.json import DjangoJSONEncoder
import json
from .ride_utils import *

def index(request):
    '''Renders the index / home page

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :return: the rendered index page using the index.html template
    :rtype: HttpResponse
    '''
    return render(request, 'index.html')

def signup(request, user_type):
    '''Renders the signup form on GET; processes the signup form on POST

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :return: the rendered SignUpForm or a redirect to homepage
    :rtype: HttpResponse
    '''
    if user_type == 'homeless':
        user_type = 'H'
    elif user_type == 'volunteer':
        user_type = 'V'
    elif user_type == 'company':
        user_type = 'C'
    else:
        return HttpResponse(status=404)
    if request.method == 'POST':
        form = SignUpForm(request.POST, user_type=user_type)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.last_name = form.cleaned_data.get('last_name')
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.car_plate = form.cleaned_data.get('car_plate', None)
            user.profile.car_make = form.cleaned_data.get('car_make', None)
            user.profile.car_model = form.cleaned_data.get('car_model', None)
            user.profile.total_volunteer_minutes = 0
            user.profile.home_address = form.cleaned_data.get('home_address', None)
            user.profile.user_type = user_type
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm(user_type=user_type)

    return render(request, 'registration/signup.html', {'form': form})

def user_type(request):
    if request.method == 'POST':
        form = UserTypeForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'H':
                return redirect('signup/homeless/')
            if user_type == 'C':
                return redirect('signup/company/')
            else:
                return redirect('signup/volunteer/')
    else:
        form = UserTypeForm()
    return render(request, 'registration/user_type.html', {'form': form})

@login_required(login_url='accounts/login/')
def dashboard(request):
    '''Renders the dashboard page for all users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the homeless.html, company.html, or volunteer.html template which matches the type of the requesting user
    :rtype: HttpResponse
    '''
    user = request.user

    if user.profile.user_type == "V":
        return volunteer(request, user)
    elif user.profile.user_type == 'H':
        return homeless(request, user)
    elif user.profile.user_type == 'C':
        return company(request, user)
    return HttpResponse(status=404)

@user_passes_test(is_homeless, login_url='/')
def homeless(request, user):
    '''Renders the dashboard page for homeless users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the homeless.html template
    :rtype: HttpResponse
    '''
    unconfirmed_rides = Ride.objects.filter(homeless = user.profile, volunteer = None, interview_datetime__gt = datetime.now()).order_by('-interview_datetime')
    confirmed_rides = Ride.objects.filter(homeless = user.profile, interview_datetime__gt = datetime.now()).exclude(volunteer = None).order_by('-interview_datetime')
    context = {'user': user, 'unconfirmed_rides': unconfirmed_rides, 'confirmed_rides': confirmed_rides}
    return render(request, 'dashboard/homeless.html', context)

@user_passes_test(is_company, login_url='/')
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

@user_passes_test(is_volunteer, login_url='/')
def volunteer(request, user):
    '''Renders the dashboard page for volunteer users

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param user_id: The id of the user whose dashboard should be rendered
    :type request: String
    :return: the rendered dashboard page for the user using the volunteer.html template
    :rtype: HttpResponse
    '''
    confirmed_rides = Ride.objects.filter(volunteer = user.profile, interview_datetime__gt = datetime.now()).order_by('-interview_datetime')
    finished_rides = Ride.objects.filter(volunteer = user.profile, interview_datetime__lte = datetime.now()).order_by('-interview_datetime')
    total_time = 0
    for ride in finished_rides:
        time = ride.end_datetime - ride.pickup_datetime
        hours = time.seconds/60/60
        total_time+=hours

    total_time = math.floor(total_time)
    context = {'user': user, 'confirmed_rides': confirmed_rides, 'finished_rides': finished_rides, 'total_time': total_time}
    return render(request, 'dashboard/volunteer.html', context)

@user_passes_test(is_homeless, login_url='/')
def job_board(request):
    '''Renders the job board page for homeless users to view jobs

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :return: the rendered job board page using the job_board.html template
    :rtype: HttpResponse
    '''

    job_posts = JobPost.objects.all().order_by('-created')

    # Extract the information we want here:
    location = request.GET.get('location', None)
    job_title = request.GET.get('job_title', None)

    # Let the query function extract the jobs we care about:
    jobs = job_utils.filterQuerySet(
        job_posts,
        location,
        job_title)

    context = {}
    context['form'] = JobBoardFilterForm(initial={
        'location': request.GET.get('location', None),
        'job_title': request.GET.get('job_title', None),
    })
    context['job_posts'] = jobs

    return render(request, 'jobs/job_board.html', context)

@user_passes_test(is_homeless, login_url='/')
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
    return render(request, 'jobs/job_detail.html', {'job': job})

@method_decorator(user_passes_test(is_homeless, login_url='/'), name='dispatch')
class RequestRideCreate(CreateView):
    '''Object used to render the ride request creation view

    :param template_name: the name of the template used to render the view
    :type template_name: string
    :param form_class: the form that specifies what data needs to be input
    :type form_class: ModelFormMetaclass
    :param queryset: the queryable attributes of the form
    :type queryset: QuerySet
    '''

    template_name = 'rides/request_ride.html'
    form_class = RideRequestForm
    def form_valid(self, form):
        form.instance.homeless = Profile.objects.get(user=self.request.user)
        self.success_url = 'dashboard'

        return super(RequestRideCreate, self).form_valid(form)
    queryset = Ride.objects.all()

@user_passes_test(lambda a: is_homeless(a) or is_volunteer(a), login_url='/')
def view_ride(request, ride_id):
    '''Renders the view that allows people experiencing homelessness to view a specific ride request
    he/she filled out, so that they can review and potentially edit the form

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param ride_id: The ride request post's idea
    :type ride_id: int
    '''
    ride_request = get_object_or_404(Ride, id=ride_id)
    context = {'ride_request': ride_request}
    return render(request, 'rides/view_ride.html', context)

@method_decorator(user_passes_test(is_homeless, login_url='/'), name='dispatch')
class RequestRideEdit(UpdateView):
    '''Object used to render the request form's update view

    :param template_name: the name of the template used to render the view
    :type template_name: string
    :param form_class: the form that specifies what data needs to be input
    :type form_class: ModelFormMetaclass
    :param queryset: the queryable attributes of the form
    :type queryset: QuerySet
    '''
    template_name = 'rides/request_ride.html'
    form_class = RideRequestForm
    queryset = Ride.objects.all()
    def get_object(self):
        id_ = self.kwargs.get("ride_id")
        self.success_url = '/view-ride/' + str(id_)
        return get_object_or_404(Ride, id=id_)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['update'] = True
        return context

@user_passes_test(is_homeless, login_url='/')
def delete_ride(request, ride_id):
    instance = Ride.objects.get(id=ride_id)
    if instance:
        homeless_id = instance.homeless.id
        user = User.objects.get(pk=homeless_id)
        instance.delete()
    return redirect('dashboard')

@user_passes_test(is_volunteer, login_url='/')
def cancel_ride(request, ride_id):
    instance = Ride.objects.get(id=ride_id)
    if instance:
        volunteer_id = instance.volunteer.id
        instance.volunteer = None
        instance.pickup_datetime = None
        instance.start_datetime = None
        instance.end_datetime = None
        instance.save()
    return redirect('dashboard')


@user_passes_test(is_company, login_url='/')
def edit_job(request, job_id):
    '''Renders the editjob form on GET; processes the editjob form on POST

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param job_id: The primary key used to index the specific job we are editing
    :type request: int
    :return: the rendered JobForm or a redirect to the company's dashboard
    :rtype: HttpResponse
    '''
    job_post = JobPost.objects.get(pk=job_id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            job_post.delete()
        else:
            form = PostJobForm(request.POST, instance=job_post)
            if form.is_valid():
                form.save()
            else:
                return render(request, 'jobs/edit_job.html', {'form': form})

        return redirect('dashboard')
    else:
        form = PostJobForm(instance=job_post)

    return render(request, 'jobs/edit_job.html', {'form': form})

@user_passes_test(is_company, login_url='/')
def post_job(request):
    '''Renders the postjob form on GET; processes the postjob form on POST

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :return: the rendered JobForm or a redirect to the company's dashboard
    :rtype: HttpResponse
    '''
    if request.method == 'POST':
        form = PostJobForm(request.POST)
        if form.is_valid():
            user = Profile.objects.get(pk=request.user.id)
            job_post = JobPost(company=user, **form.cleaned_data)
            job_post.save()
            return redirect('dashboard')
    else:
        form = PostJobForm()

    return render(request, 'jobs/post_job.html', {'form': form})

@user_passes_test(is_volunteer, login_url='/')
def ride_board(request):
    rides = Ride.objects.filter(volunteer=None)
    start_datetime = request.GET.get('start_datetime', None)
    end_datetime = request.GET.get('end_datetime', None)
    max_range = request.GET.get('max_range', None)
    profile = Profile.objects.get(user=request.user)

    rides = filterQuerySet(
        rides,
        start_datetime,
        end_datetime,
        max_range,
        profile.home_address)

    context = {}
    context['form'] = FilterForm(initial={
        'start_time': request.GET.get('start_datetime', None),
        'end_time': request.GET.get('end_datetime', None),
        'max_range': request.GET.get('max_range', None),
        'start_address': request.GET.get('start_address', None),
    })
    context['GOOGLE_MAPS_API_KEY'] = GOOGLE_MAPS_API_KEY
    context['rides'] = rides


    context['rides_json'] = json.dumps(list(getRideDict(ride) for ride in rides), cls=DjangoJSONEncoder)

    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    home_info = gmaps.geocode(request.user.profile.home_address)
    if home_info:
        location = home_info[0]['geometry']['location']
        context['home'] = location

    return render(request, 'rides/ride_board.html', context=context)

@user_passes_test(is_volunteer, login_url='/')
def confirm_ride(request, ride_id):
    ride = Ride.objects.get(pk=ride_id)
    homeless_profile = ride.homeless
    volunteer_profile = Profile.objects.get(user=request.user)
    ride.volunteer = volunteer_profile
    td_vec = getTimeDistanceVector(
        volunteer_profile.home_address,
        homeless_profile.home_address,
        ride.interview_address,
        ride.interview_duration
    )
    if td_vec == None:
        return redirect('search_rides')
    ride.distance = getDistance(td_vec)
    times = [time for (time, _) in td_vec]
    ride.start_datetime, ride.pickup_datetime, ride.end_datetime, _ = getTimes(td_vec, ride.interview_datetime)
    ride.save()

    return redirect('dashboard')
