from django.db import models
from .appuser import AppUser
from django.conf import settings
#出行计划
class Plan(models.Model):
    owner = models.ForeignKey(AppUser,on_delete = models.CASCADE)
    content = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
#转成json传给前端的序列类型
class Plan_Ser(models.Model):
    type = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    id1 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    type1 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    from1 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    to1 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    id2 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    type2 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    from2 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    to2 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)

class Plan_Comp(models.Model):
    person1 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    person2 = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)
    content = models.TextField(null=True, default=None, max_length=settings.MAX_MESSAGE_CONTENT_LENGTH)