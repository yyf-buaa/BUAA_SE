from django.db import models
from django.conf import settings

from utilities import uuid, date

from .appuser import AppUser
from .position import Position


class Traffic(models.Model):
    departure = models.OneToOneField(Position, related_name='departure_position', on_delete=models.CASCADE)
    destination = models.OneToOneField(Position, related_name='destination_position', on_delete=models.CASCADE)
    type = models.IntegerField(default=settings.TRAFFIC_TRAIN)
    price = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class PickTraffic(models.Model):
    date = models.DateField(auto_now=True)
    owner = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='pick_traffic')
    traffic = models.ForeignKey(Traffic, on_delete=models.CASCADE, related_name='picked_traffic')

