from django.db import models
from django.conf import settings

from utilities import uuid
from .images import Image


class Position(models.Model):
    id = models.CharField(max_length=6, primary_key=True) # adcode
    name = models.CharField(max_length=32, default='')
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    description = models.TextField(default='')
    cover = models.ForeignKey(Image, related_name='positions', null=True, on_delete=models.CASCADE)
    images = models.ManyToManyField(Image, related_name='position_owner')
    visibility = models.BooleanField(default=False)


class EpidemicControlInfo(models.Model):
    description = models.TextField(default='')
    time = models.DateTimeField(auto_now_add=True)
    position = models.ForeignKey(Position, related_name='epidemic', on_delete=models.CASCADE)