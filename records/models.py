from django.db import models

from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

class Record(models.Model):
    user_id = models.IntegerField()
    text = models.CharField(max_length=5000)
    category = models.CharField(max_length=32)
    location_x = models.FloatField(default=0)
    location_y = models.FloatField(default=0)
    address = models.CharField(max_length=255, default=0)
    datetime = models.DateTimeField(default=timezone.now, null=True)
    done = models.BooleanField(default=False)
    condition = models.CharField(max_length=16)
    calendar_id = models.CharField(max_length=255, default=0)

class Token(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=255, default=0)
    is_authorized = models.BooleanField(default=False)
