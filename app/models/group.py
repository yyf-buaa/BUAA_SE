from django.db import models
from django.db.models import Sum, F
from django.conf import settings

from utilities import uuid

from .appuser import AppUser
from .address import Address
from .images import Image
from .companion import Companion
from utilities import date


class Group(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    # 群主项有必要么?
    # owner = models.ForeignKey(AppUser, null=True, blank=True, on_delete=models.SET_NULL)
    companion = models.ForeignKey(Companion, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.TextField(default='Group chat', max_length=settings.MAX_GROUP_NAME_LENGTH)


class InGroup(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    # 群删除所有表项都删除，用户删除也从群信息里删除?
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    person = models.ForeignKey(AppUser, on_delete=models.CASCADE)