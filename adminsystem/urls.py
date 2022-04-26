from django.urls import path, include
from rest_framework import routers as rest_routers

from django.conf import settings
from .apis import *
from main import routers

ROUTER = routers.TravelRouter()
ROUTER.register(r'users', UserApis)
ROUTER.register(r'travels', TravelApis)
ROUTER.register(r'comments', CommentApis)
ROUTER.register(r'position', PositionApis)
ROUTER.register(r'messages', MessageApis)
ROUTER.register(r'companions', CompanionApis)
ROUTER.register(r'images', ImageApis)
ROUTER.register(r'adminmessages', AdminMessageApis)
ROUTER.register(r'ads', AdvertisementApis)

urlpatterns = [
    path('', include(ROUTER.urls)),
]
