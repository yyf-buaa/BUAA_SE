from django.db import models
from django.conf import settings

from utilities import uuid, date
from .position import Position
from .appuser import AppUser
from .travel import Travel
from .companion import Companion


class Tag(models.Model):
    # tag名
    content = models.CharField(max_length=50, default='')
    # 请求人
    user = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True, default=None)
    # 阅读量
    read = models.IntegerField(default=0)
    # 审核状态
    forbidden = models.IntegerField(default=settings.TAG_FORBIDDEN_PENDING)
    forbidden_reason = models.TextField(default='')
    date = models.DateField(auto_now=True)



class TagOnTravel(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='taggedTravel')
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE, related_name='travelTags')
    #type表示是否在文中，1表示为文中tag，0表示为文末tag
    type = models.IntegerField(default=0)

class TagOnCompanion(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='taggedCompanion')
    companion = models.ForeignKey(Companion, on_delete=models.CASCADE, related_name='CompanionTags')
    #type表示是否在文中，1表示为文中tag，0表示为文末tag
    type = models.IntegerField(default=0)