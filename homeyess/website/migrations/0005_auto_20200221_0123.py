# Generated by Django 3.0.3 on 2020-02-21 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_riderequestpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='riderequestpost',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Optional', max_length=20),
        ),
        migrations.AddField(
            model_name='riderequestpost',
            name='pickup_time',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='riderequestpost',
            name='interview_duration',
            field=models.CharField(help_text='in minutes', max_length=20),
        ),
    ]