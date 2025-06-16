from django.db import models

from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

class Record(models.Model):
    user_id = models.IntegerField()
    text = models.CharField(max_length=5000)
    category = models.CharField(max_length=32)
    location_x = models.FloatField()
    location_y = models.FloatField()
    datetime = models.DateTimeField(default=timezone.now)
    done = models.BooleanField(default=False)
    condition = models.CharField(max_length=16)
