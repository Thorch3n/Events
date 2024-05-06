# Generated by Django 5.0.4 on 2024-05-05 14:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='end_datetime',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='start_datetime',
            new_name='start_date',
        ),
        migrations.AddField(
            model_name='event',
            name='registered_users',
            field=models.ManyToManyField(blank=True, related_name='events_registered', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]