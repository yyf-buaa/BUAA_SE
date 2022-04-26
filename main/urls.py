"""travel_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
import re
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.urls import re_path
from django.views.static import serve

from django.conf import settings

from . import user
from .routers import TravelRouter

from . import utils

ROUTER = TravelRouter()
ROUTER.register(r'user', user.UserView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(ROUTER.urls)),
    path('api/token-auth/', TokenObtainPairView.as_view()),
    path('api/token-refresh/', TokenRefreshView.as_view()),
    path('api/core/', include('app.urls')),
    path('api/admin/', include('adminsystem.urls')),
    re_path(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')), serve,
            kwargs={'document_root': os.path.join(settings.MEDIA_ROOT, 'system')}),
]

if not settings.APP_SHOW_STATUS:
    @api_view(http_method_names=['GET'])
    def status(request):
        return Response(200)

    urlpatterns.extend([
        path('api/status/', status),
    ])

urlpatterns.extend([
])
