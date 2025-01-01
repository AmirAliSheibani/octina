from django.conf import settings
from django.db import models

# Create your models here.
User = settings.AUTH_USER_MODEL

class Location(models.Model):
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_Location', blank=True,
                                   null=True)