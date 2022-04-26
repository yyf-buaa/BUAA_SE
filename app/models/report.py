from django.db import models
from django.db.models import Sum, F
from django.conf import settings

from utilities import uuid

from .appuser import AppUser
from .address import Address
from .images import Image
from utilities import date


class Report(models.Model):
    """
    Foreign keys:

    collectors - AppUser
    """
    # 举报人
    userId = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING, null=True)
    # 文字描述
    description = models.TextField(default='', max_length=settings.MAX_REPORT_DESCRIPTION_LENGTH)
    # 图片描述
    images = models.ManyToManyField(Image, related_name='reports')
    # 处理结果
    result = models.IntegerField(default=settings.REPORT_RESULT_PENDING)
