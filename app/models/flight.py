from django.db import models
from django.conf import settings

from utilities import uuid, date
from .position import Position


class Flight(models.Model):
    flightno = models.CharField(max_length=10, default='')
    # 真实承运人
    realflightno = models.CharField(max_length=10, default='')
    airline = models.TextField(default='')
    # 出发/到达城市及代码
    city = models.TextField(default='')
    city_code = models.CharField(max_length=10, default='')
    endcity = models.TextField(default='')
    endcity_code = models.CharField(max_length=10, default='')

    # 机场及代码
    departport = models.TextField(default='')
    departport_code = models.TextField(default='')
    arrivalport = models.TextField(default='')
    arrivalport_code = models.TextField(default='')
    # 航站楼
    departterminal = models.TextField(default='')
    arrivalterminal = models.TextField(default='')

    # 日期和时间
    departdate = models.DateField()
    departtime = models.TimeField()
    arrivaldate = models.DateField()
    arrivaltime = models.TimeField()
    arrivaldateadd = models.IntegerField(default=0)

    # 飞机型号
    craft = models.CharField(max_length=10, default='')
    # 经停站数
    stopnum = models.IntegerField(default=0)
    # 耗时
    costtime = models.TimeField()
    # 赚准点率95~95%
    punctualrate=models.IntegerField(default=100)

    minprice = models.IntegerField()
    airporttax = models.IntegerField()
    fueltax = models.IntegerField()
    # 有无餐食
    food = models.BooleanField(default=False)
    # ASR支持标志
    isasr = models.BooleanField(default=False)
    # 电子票
    iseticket = models.BooleanField(default=False)
    # 代码共享
    iscodeshare = models.BooleanField(default=False)


class FlightPriceList(models.Model):
    owner = models.ForeignKey(Flight, on_delete=models.CASCADE)
    cabinname = models.TextField(default='')
    cabincode = models.CharField(max_length=2)
    price = models.IntegerField(default=0)
    discount = models.IntegerField(default=100)

