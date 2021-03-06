"""
homeyess/website/models.py
"""
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Model to store information about a user

    :param user: the authentication object containing username, password, email (optional), first / last name
    :type user: User
    :param phone: the user's phone number
    :type phone: (optional) CharField / string
    :param user_type: the type of user (volunteer, homeless, company)
    :type user_type: UserType
    :param car_plate: the license plate number of the volunteer's car (only required for volunteer)
    :type car_plate: (optional) CharField / string
    :param car_make: the make of the volunteer's car (only required for volunteer)
    :type car_make: (optional) CharField / string
    :param car_model: the model of the volunteer's car (only required for volunteer)
    :type car_model: (optional) CharField / string
    :param total_volunteer_minutes: the total amount of time a volunteer has volunteered
    :type total_volunteer_minutes: int
    :param home_address: home address (only required for volunteer)
    :type home_address: CharField / string
    """
    class UserType(Enum):
        """Enum to represent types of users: Volunteer, Homeless, Company
        """
        Volunteer = "V"
        Homeless = "H"
        Company = "C"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # user contains email, first_name (or comapny name), last_name
    phone = models.CharField(max_length=10, blank=True)
    user_type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in UserType], default=UserType.Homeless)

    # these should only be populated if user_type == UserType.Volunteer
    car_plate = models.CharField(max_length=8, blank=True, null=True)
    car_make = models.CharField(max_length=20, blank=True, null=True)
    car_model = models.CharField(max_length=20, blank=True, null=True)
    total_volunteer_minutes = models.IntegerField(blank=True, null=True)
    home_address = models.CharField(max_length=200, blank=True, null=True)


class Ride(models.Model):
    """Model to store information about a ride request. Contains start / end time and location, the homeless person, and a volunteer if the ride has already been confirmed.
    Note that the object should be created when a ride request is made and altered when the request is updated (by homeless) or confirmed (by user).

    :param homeless: the user who requested the ride
    :type homeless: User
    :param volunteer: the user who volunteered to give the ride
    :type volunteer: (optional) User
    :param interview_datetime: the date and time of the interview
    :type interview_datetime: DateTime
    :param interview_duration: the time in minutes that the interview should last
    :type interview_duration: int
    :param interview_address: the address of the interview
    :type interview_address: CharField / string
    :param interview_company: the company hosting the interview
    :type interview_company: CharField / string
    :param start_datetime: the time the volunteer leaves their house
    :type start_datetime: DateTime
    :param pickup_datetime: the date and time the homeless person should be picked up for their interview
    :type pickup_datetime: DateTime
    :param end_datetime: the time the volunteer arrives back at their house
    :type end_datetime: DateTime
    """

    def get_absolute_url(self):
        """Returns the path to view a specific ride request that was just created/edited

        :return: a string of the path to view the created/modified ride request
        :rtype: string
        """
        return "/ViewRideForm/" + str(self.id)

    def get_fields(self):
        """Returns a list of attributes of the Ride object, used for the ViewRideForm template

        :return: A list of tuples that contain (field_name, field_value)
        :rtype: List[(string, string)]
        """
        return [(field.name, field.value_to_string(self)) for field in Ride._meta.fields]


    homeless = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="ride_homeless_set")
    volunteer = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True, related_name="ride_volunteer_set")
    interview_datetime = models.DateTimeField()
    interview_duration = models.IntegerField()
    interview_address = models.CharField(max_length=200)
    interview_company = models.CharField(max_length=100)
    start_datetime = models.DateTimeField(null=True, blank=True)
    pickup_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

class JobPost(models.Model):
    """Model to store information about a job post

    :param company: the company that made the post
    :type company: User
    :param created: the date the post was created
    :type created: Date
    :param last_edited: the date the post was last edited
    :type last_edited: Date
    :param location: the location of the job (city, county, etc.)
    :type location: CharField / string
    :param wage: how much the job will pay (can be hourly, salary, etc.)
    :type wage: CharField / string
    :param hours: the time commitment of the job
    :type hours: CharField / string
    :param job_title: the title of the job (e.g. janitor)
    :type job_title: CharField / string
    :param short_summary: a short summary of the job description
    :type short_summary: CharField / string
    :param description: the job description (should include instruction to apply)
    :type description: Text / string
    """
    company = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created = models.DateField(auto_now_add=True)
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
