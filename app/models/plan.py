from django.db import models
from .appuser import AppUser
from django.conf import settings
#出行计划
class Plan(models.Model):
    owner = models.ForeignKey(AppUser,on_delete = models.CASCADE)
    content = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)