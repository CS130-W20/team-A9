# Generated by Django 3.0.3 on 2020-03-07 22:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import website.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=10)),
                ('user_type', models.CharField(choices=[('V', 'Volunteer'), ('H', 'Homeless'), ('C', 'Company')], default=website.models.Profile.UserType['Homeless'], max_length=100)),
                ('car_plate', models.CharField(blank=True, max_length=8, null=True)),
                ('car_make', models.CharField(blank=True, max_length=20, null=True)),
                ('car_model', models.CharField(blank=True, max_length=20, null=True)),
                ('total_volunteer_minutes', models.IntegerField(blank=True, null=True)),
                ('home_address', models.CharField(blank=True, max_length=200, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interview_datetime', models.DateTimeField()),
                ('interview_duration', models.IntegerField()),
                ('interview_address', models.CharField(max_length=200)),
                ('interview_company', models.CharField(max_length=100)),
                ('start_datetime', models.DateTimeField(blank=True, null=True)),
                ('pickup_datetime', models.DateTimeField(blank=True, null=True)),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('homeless', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ride_homeless_set', to='website.Profile')),
                ('volunteer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ride_volunteer_set', to='website.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='JobPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_edited', models.DateField(auto_now=True)),
                ('location', models.CharField(max_length=100)),
                ('wage', models.CharField(max_length=100)),
                ('hours', models.CharField(max_length=100)),
                ('job_title', models.CharField(max_length=100)),
                ('short_summary', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Profile')),
            ],
        ),
    ]