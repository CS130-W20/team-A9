from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from enum import Enum


class Profile(models.Model):
	class UserType(Enum):
		Volunteer = 'V'
		Homeless = 'H'
		Company = 'C'

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	# user contains email, first_name (or comapny name), last_name
	phone = models.CharField(max_length=10, blank=True)
	user_type = models.CharField(max_length=100, choices=[(tag, tag.value) for tag in UserType], default=UserType.Homeless)

	# these should only be populated if user_type == UserType.Volunteer
	car_plate = models.CharField(max_length=8, blank=True, null=True)
	car_make = models.CharField(max_length=20, blank=True, null=True)
	car_model = models.CharField(max_length=20, blank=True, null=True)
	total_volunteer_minutes = models.IntegerField()


class Ride(models.Model):
	homeless = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ride_homeless_set')
	volunteer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='ride_volunteer_set')
	interview_datetime = models.DateTimeField()
	interview_duration = models.IntegerField()
	volunteer_address = models.CharField(max_length=200, null=True)
	pickup_address = models.CharField(max_length=200)
	pickup_datetime = models.DateTimeField()
	interview_address = models.CharField(max_length=200)
	interview_company = models.CharField(max_length=100)
	end_datetime = models.DateTimeField()
	class RideStatus(Enum):
		Unconfirmed = 'U'
		Confirmed = "C"
		Finished = "F"
	ride_status = models.CharField(max_length=100, choices=[(tag, tag.value) for tag in RideStatus], default=RideStatus.Unconfirmed)

class JobPost(models.Model):
	company = models.ForeignKey(Profile, on_delete=models.CASCADE)
	last_edited = models.DateField(auto_now=True)
	location = models.CharField(max_length=100)
	wage = models.CharField(max_length=100)
	hours = models.CharField(max_length=100)
	job_title = models.CharField(max_length=100)
	short_summary = models.CharField(max_length=200)
	description = models.TextField()

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
