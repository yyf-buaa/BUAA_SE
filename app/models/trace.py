from django.db import models
from django.conf import settings

from utilities import uuid, date

from .appuser import AppUser
from .traffic import Traffic


class Trace(models.Model):
    date = models.DateField(auto_now=True)
    owner = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='trace')
    traffic = models.ForeignKey(Traffic, on_delete=models.CASCADE, related_name='traffic')

