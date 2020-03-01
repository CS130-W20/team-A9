"""
homeyess/website/views.py
"""
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Ride, JobPost
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from website.forms import SignUpForm, RideRequestForm, PostJobForm
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

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
    user = User.objects.get(pk=user_id)
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
    def form_valid(self, form):
        print("form data: {}".format(form.data))
        form.instance.homeless = Profile.objects.get(user=self.request.user)
        form.instance.pickup_datetime = "2020-01-20 00:00"
        form.instance.end_datetime = "2020-01-20 00:00"
        return super(RequestRideCreate, self).form_valid(form)
    queryset = Ride.objects.all()



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
    else:
        return index(request)

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
