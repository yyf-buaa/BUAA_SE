from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied
from rest_framework.decorators import action

from app.response import *
from app.models import AppUser
from adminsystem.serializers import UserSerializer
from utilities.conversion import get_list
from utilities import filters

class UserApis(viewsets.ModelViewSet):
    filter_backends = [filters.QueryFilterBackend.custom(
        ('name', 'name', 'contains'),
        ('nickname', 'nickname', 'contains'),
        ('id', 'id', 'exact'),
    ordering_rule='-time')]
    permission_classes = [permissions.IsAuthenticated]
    queryset = AppUser.objects.all()
    serializer_class = UserSerializer

    def bulk_destroy(self, request, *args, **kwargs):
        ids = get_list(request.data, 'id')
        objs = self.get_queryset().filter(id__in=ids)
        objs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

