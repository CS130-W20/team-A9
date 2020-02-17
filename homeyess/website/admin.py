from django.contrib import admin

from .models import Profile, Ride, JobPost

admin.site.register(Profile)
admin.site.register(Ride)
admin.site.register(JobPost)
