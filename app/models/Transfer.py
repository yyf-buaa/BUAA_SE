from django.db import models
from django.conf import settings

from utilities import uuid, date
from .position import Position
class Transfer(models.Model):
    id1 = models.TextField(default='')
    type1 = models.TextField(default='')
    id2 = models.TextField(default='')
    type2 = models.TextField(default='')
