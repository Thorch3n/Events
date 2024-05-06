from django.contrib.auth.models import User
from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    registered_users = models.ManyToManyField(User, related_name='events_registered', blank=True)

    def __str__(self):
        return self.title