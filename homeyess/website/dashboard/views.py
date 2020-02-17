from django.shortcuts import render
from .models import Profile, Ride, JobPost

def homeless(request):
    user = Profile.objects.get(username=request.username)
    unconfirmed_rides = Ride.objects.get(homeless = user, ride_status = "U")
    confirmed_rides = Ride.objects.get(homeless = user, ride_status = "C")
    context = {'user': user, 'unconfirmed_rides': unconfirmed_rides, 'confirmed_rides': confirmed_rides}
    return render(request, 'dashboard/homeless.html', context)

def company(request):
    user = Profile.objects.get(username=request.username)
    job_posts = JobPost.objects.get(company=user)
    context = {'user': user, 'job_posts': job_posts}
    return render(request, 'dashboard/company.html', context)

def volunteer(request):
    user = Profile.objects.get(username=request.username)
    confirmed_rides = Ride.objects.get(volunteer = user, ride_status = "C")
    finished_rides = Ride.objects.get(volunteer = user, ride_status = "F")
    context = {'user': user, 'confirmed_rides': confirmed_rides, 'finished_rides': finished_rides}
    return render(request, 'dashboard/volunteer.html', context)
