from django.db import models
from django.conf import settings

from utilities import uuid, date
from .position import Position


class Train(models.Model):
    trainno = models.CharField(max_length=10, default='')
    departstation = models.TextField(default='')
    terminalstation = models.TextField(default='')
    type = models.CharField(max_length=2, default="0")
    typename = models.TextField(default='')

    # 起止站
    station = models.TextField(default='')
    endstation = models.TextField(default='')

    # 日期和时间
    departdate = models.DateField()
    departtime = models.TimeField()
    arrivaldate = models.DateField()
    arrivaltime = models.TimeField()
    day = models.IntegerField(default=0)

    # 经停站数
    stopnum = models.IntegerField(default=0)
    # 耗时
    costtime = models.TextField(default='')


class TrainPriceList(models.Model):
    owner = models.ForeignKey(Train, related_name='prices', on_delete=models.CASCADE)
    type = models.TextField(default='硬座')
    price = models.FloatField(default=0)