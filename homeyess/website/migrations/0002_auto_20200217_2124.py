# Generated by Django 3.0.3 on 2020-02-17 21:24

from django.db import migrations, models
import django.db.models.deletion
import website.models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='car_make',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='car_model',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='car_plate',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='user_type',
            field=models.CharField(choices=[('V', 'Volunteer'), ('H', 'Homeless'), ('C', 'Company')], default=website.models.Profile.UserType['Homeless'], max_length=100),
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interview_datetime', models.DateTimeField()),
                ('interview_duration', models.IntegerField()),
                ('volunteer_address', models.CharField(max_length=200, null=True)),
                ('pickup_address', models.CharField(max_length=200)),
                ('interview_address', models.CharField(max_length=200)),
                ('homeless', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ride_homeless_set', to='website.Profile')),
                ('volunteer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ride_volunteer_set', to='website.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='JobPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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