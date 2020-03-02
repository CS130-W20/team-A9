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

from website.forms import SignUpForm, RideRequestForm, PostJobForm, FilterForm
from .models import Profile, Ride, JobPost
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import googlemaps
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from .decorators import is_homeless, is_volunteer, is_company
import requests
from homeyess.settings import GOOGLE_MAPS_API_KEY
import functools
from django.conf import settings
import math
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.forms.models import model_to_dict
import pytz

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

@login_required(login_url='accounts/login/')
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
    return render(request, 'job_board/job_board.html', {'job_posts': job_posts})

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
    return render(request, 'job_board/job_detail.html', {'job': job})

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

    template_name = 'ride_request/request_ride.html'
    form_class = RideRequestForm
    def form_valid(self, form):
        print("form data: {}".format(form.data))
        form.instance.homeless = Profile.objects.get(user=self.request.user)
        form.instance.pickup_datetime = "2020-01-20 00:00"
        form.instance.end_datetime = "2020-01-20 00:00"
        return super(RequestRideCreate, self).form_valid(form)
    queryset = Ride.objects.all()



@user_passes_test(is_homeless, login_url='/')
def viewrideform(request, post_id):
    '''Renders the view that allows people experiencing homelessness to view a specific ride request
    he/she filled out, so that they can review and potentially edit the form

    :param request: The http request containing user information or extra arguments
    :type request: HttpRequest
    :param post_id: The ride request post's idea
    :type post_id: int
    '''
    form_set = Ride.objects.filter(id=post_id)
    if form_set:
        form = form_set[0]
    else:
        form = []
    context = {'form': form}
    return render(request, 'ride_request/ViewRideForm.html', context)

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
	template_name = 'ride_request/request_ride.html'
	form_class = RideRequestForm
	queryset = Ride.objects.all()

	def get_object(self):
		id_ = self.kwargs.get("post_id")
		return get_object_or_404(Ride, id=id_)

def DeleteRideRequest(request, post_id):
    instance = Ride.objects.get(id=post_id)
    if instance:
        homeless_id = instance.homeless.id
        print(homeless_id)
        user = User.objects.get(pk=homeless_id)
        instance.delete()
    return redirect('/dashboard/' + str(homeless_id))

@user_passes_test(is_company, login_url='/')
def editjob(request, job_id):
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
                return render(request, 'jobs/editjob.html', {'job_id': job_id, 'form': form})

        user = Profile.objects.get(pk=request.user.id)
        job_posts = JobPost.objects.filter(company=user)
        context = {'user': user, 'job_posts': job_posts}
        return render(request, 'dashboard/company.html', context)
    else:
        form = PostJobForm(instance=job_post)

    return render(request, 'jobs/editjob.html', {'form': form})

@user_passes_test(is_company, login_url='/')
def postjob(request):
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
            job_posts = JobPost.objects.filter(company=user)
            context = {'user': user, 'job_posts': job_posts}
            return render(request, 'dashboard/company.html', context)
    else:
        form = PostJobForm(initial={'wage': '15.50 usd/hr', 'hours': '40 hr/wk'})

    return render(request, 'jobs/postjob.html', {'form': form})

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
    context['rides_json'] = json.dumps(list(model_to_dict(ride) for ride in rides), cls=DjangoJSONEncoder)
    context['rides'] = rides

    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    home_info = gmaps.geocode(request.user.profile.home_address)
    if home_info:
        location = home_info[0]['geometry']['location']
        context['home'] = location

    return render(request, 'ride_board.html', context=context)

def confirmRide(request, ride_id):
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

    return redirect('search_rides')

def filterQuerySet(rides, start_datetime, end_datetime, max_range, v_start):
    for ride in rides:
        td_vec = getTimeDistanceVector(
            ride.homeless.home_address,
            v_start,
            ride.interview_address,
            ride.interview_duration
        )
        if td_vec == None:
            ride.d = None
            ride.sd = None
            ride.ed = None
        else:
            ride.d = getDistance(td_vec)
            ride.sd, _, ride.ed, ride.total_time = getTimes(td_vec, ride.interview_datetime)

        #set pickup lat/long
        # pickup_info = self.gmaps.geocode(ride.homeless.home_address)
        # if pickup_info:
        #     location = pickup_info[0]['geometry']['location']
        #     ride.pickup_location = (location['lat'], location['lng'])

    rides = [ride for ride in rides if ride.d != None]
    if start_datetime:
        start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
        start_datetime = pytz.utc.localize(start_datetime)
        rides = [ride for ride in rides if ride.sd >= start_datetime]
    if end_datetime:
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M')
        end_datetime = pytz.utc.localize(end_datetime)
        rides = [ride for ride in rides if ride.ed <= end_datetime]
    if max_range:
        max_range = int(max_range)
        rides = [ride for ride in rides if ride.d <= max_range]

    return rides

def getTimeDistanceVector(v_start, hp_start, interview_location, interview_duration):
    URL = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    PARAMS = {
        'key': GOOGLE_MAPS_API_KEY,
        'origins': v_start + '|' + hp_start + '|' + interview_location,
        'destinations': v_start + '|' + hp_start + '|' + interview_location,
    }

    data = getResponseJson(URL, PARAMS)

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

        time_distance_vector.append((time_in_minutes, distance_in_miles))

    # insert the interview in between the driving
    time_distance_vector.insert(2, (interview_duration, 0))
    return time_distance_vector

def getResponseJson(url, params):
    r = requests.get(url=url, params=params)
    return r.json()


def getDistance(vec):
    distances = [distance for (_, distance) in vec]
    dist = functools.reduce(lambda a, b: a + b, distances)
    dist = int(dist)
    return dist

def getTimes(vec, interview_datetime):
    pickup_datetime = interview_datetime - timedelta(minutes=vec[1][0])
    start_datetime = pickup_datetime - timedelta(minutes=vec[0][0])
    times = [time for (time, _) in vec]
    total_time = functools.reduce(lambda a, b: a + b, times)
    total_time_string = getTimeString(int(total_time))
    end_datetime = start_datetime + timedelta(minutes=total_time)
    return start_datetime, pickup_datetime, end_datetime, total_time_string

def getTimeString(mins):
    s = ""
    hours = mins//60
    m = mins%60
    if hours > 0:
        s += str(hours) + ' hrs '
    if m > 0:
        s += str(m) + ' min'
    return s
