from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from app.models import *
from adminsystem.serializers import *
from app.response import *
from utilities import conversion, filters, permission as _permission
from utilities import conversion, filters
class TagApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(methods=['GET'], detail=False, url_path='getTagList')
    def getTagList(self, request, *args, **kwargs):
        if 'forbidden' not in request.GET:
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                tags_ser = TagSerializer(page, many=True)
                return self.get_paginated_response(tags_ser.data)
            else:
                tags_ser = TagSerializer(self.queryset, many=True)
                return Response(tags_ser.data, status=status.HTTP_200_OK)
        else:
            forbidden = request.GET.get('forbidden')
            tags = Tag.objects.filter(forbidden=forbidden)
            page = self.paginate_queryset(tags)
            if page is not None:
                tags_ser = TagSerializer(page,many = True)
                return self.get_paginated_response(tags_ser.data)
            else:
                tags_ser = TagSerializer(tags,many = True)
                return Response(tags_ser.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='changeTagStatus')
    def changeTagStatus(self, request, *args, **kwargs):
        id = request.data.get('id')
        forbidden = request.data.get('forbidden')
        forbidden_reason = request.data.get('forbidden_reason')
        if forbidden == 0 or forbidden == 2:
            tag_set = Tag.objects.filter(id = id)
            tag_set.update(forbidden=forbidden)
        elif forbidden == 1:
            tag_set = Tag.objects.filter(id=id)
            tag_set.update(forbidden=forbidden,forbidden_reason=forbidden_reason)
        return Response(True, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='deleteTag')
    def deleteTag(self, request, *args, **kwargs):
        id = request.data.get('id')
        tag_set = Tag.objects.filter(id=id)
        tag_set.delete()
        return Response(True, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='getTravelTags')
    def getTravelTags(self, request, *args, **kwargs):
        travel_id = request.GET.get('travel_id')
        travel = Travel.objects.filter(id = travel_id).first()
        tag_set = TagOnTravel.objects.filter(travel=travel)
        tag_ser = TagOnTravelSerializer(tag_set,many=True)
        return Response(tag_ser.data,status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='getCompanionTags')
    def getCompanionTags(self, request, *args, **kwargs):
        companion_id = request.GET.get('companion_id')
        companion = Companion.objects.filter(id=companion_id).first()
        tag_set = TagOnCompanion.objects.filter(companion=companion)
        tag_ser = TagOnCompanionSerializer(tag_set, many=True)
        return Response(tag_ser.data, status=status.HTTP_200_OK)




