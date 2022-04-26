from django.db import models
from django.conf import settings
from .appuser import AppUser
from .position import Position
class BlackPos(models.Model):
    person = models.ForeignKey(AppUser,on_delete = models.CASCADE)
    position = models.ForeignKey(Position,on_delete=models.CASCADE)
