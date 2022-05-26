from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied
from rest_framework.decorators import action
from django.conf import settings

from app.models import Tag, TagOnTravel, TagOnCompanion,Companion,Travel
from app.serializers import TagSerializer, TagOnTravelSerializer, TagOnCompanionSerializer, TagAndTravelSerializer, TagAndCompanionSerializer
import datetime

from django.db.models import QuerySet
from app.utilities import permission
from app.response import *
from utilities import conversion, filters, permission as _permission


class TagApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
              viewsets.mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
              viewsets.mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(methods=['GET'], detail=False, url_path='getTagRead')
    def getTags(self, request, *args, **kwargs):
        content = request.GET.get('content')
        tag = Tag.objects.filter(content=content)
        if tag:
            tag = tag.first()
            return Response({'read': tag.read}, status=status.HTTP_200_OK)
        return Response('tag未创建', status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['GET'], detail=False, url_path='searchTaggedTravels')
    def getTaggedTravel(self, request, *args, **kwargs):
        content = request.GET.get('content')
        request_user = _permission.user_check(request)
        tag = Tag.objects.filter(content=content)
        if tag:
            tag = tag.first()
            if not tag.forbidden == 0:
                return Response('tag不可见（待审核或未通过）', status=status.HTTP_400_BAD_REQUEST)
            setattr(tag, 'read', tag.read + 1)
            tag.save()
            travels = TagOnTravel.objects.filter(tag=tag, travel__visibility=settings.TRAVEL_VISIBILITIES_DEFAULT,
                                                 travel__forbidden=settings.TRAVEL_FORBIDDEN_FALSE)
            travel_private = TagOnTravel.objects.filter(tag=tag,
                                                        travel__visibility=settings.TRAVEL_VISIBILITIES_PRIVATE,
                                                        travel__forbidden=settings.TRAVEL_FORBIDDEN_FALSE,
                                                        travel__owner_id=request_user)
            travels = travel_private | travels
            travels = travels.order_by('travel__read_total')
            if not travels:
                return Response('无数据', status=status.HTTP_204_NO_CONTENT)
            page = self.paginate_queryset(travels)
            if page is not None:
                serializer = TagAndTravelSerializer(page, many=True)
                datas = serializer.data
                for data, obj in zip(datas, page):
                    if request_user > 0:
                        data['travel']['liked'] = 1 if obj.travel.likes.filter(id=request_user) else 0
                    else:
                        data['travel']['liked'] = 0
                #for data in datas:
                #    if request_user > 0:
                #        data['travel']['liked'] = 1 if data['travel']['owner']['id'] == request_user else 0
                #    else:
                #        data['travel']['liked'] = 0
                return self.get_paginated_response(datas)
            serializer = TagAndTravelSerializer(travels, many=True)
            datas = serializer.data
            for data, obj in zip(datas, travels):
                if request_user > 0:
                    data['travel']['liked'] = 1 if obj.travel.likes.filter(id=request_user) else 0
                else:
                    data['travel']['liked'] = 0
            #for data in datas:
            #    if request_user > 0:
            #        data['travel']['liked'] = 1 if data['travel']['owner']['id'] == request_user else 0
            #    else:
            #        data['travel']['liked'] = 0
            return Response(datas)
        return Response('tag未创建', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='searchTaggedCompanions')
    def getTaggedCompanion(self, request, *args, **kwargs):
        content = request.GET.get('content')
        tag = Tag.objects.filter(content=content)
        if tag:
            tag = tag.first()
            if not tag.forbidden == 0:
                return Response('tag不可见（待审核或未通过）', status=status.HTTP_400_BAD_REQUEST)
            setattr(tag, 'read', tag.read + 1)
            tag.save()
            companions = TagOnCompanion.objects.filter(tag=tag, companion__forbidden=settings.TRAVEL_FORBIDDEN_FALSE)
            if not companions:
                return Response('无数据', status=status.HTTP_204_NO_CONTENT)
            page = self.paginate_queryset(companions)
            if page is not None:
                serializer = TagAndCompanionSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = TagAndCompanionSerializer(companions, many=True)
            return Response(serializer.data)
        return Response('tag未创建', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='getTravelTags')
    def getTravelTags(self, request, *args, **kwargs):
        travel_id = request.GET.get('travel_id')
        travel = Travel.objects.filter(id = travel_id).first()
        tag_set = TagOnTravel.objects.filter(travel=travel)
        tag_val_set = []
        for tagOnTravel in tag_set:
            if tagOnTravel.tag.forbidden == 0:
                tag_val_set.append(tagOnTravel)
        tag_ser = TagOnTravelSerializer(tag_val_set,many=True)
        return Response(tag_ser.data,status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='getCompanionTags')
    def getCompanionTags(self, request, *args, **kwargs):
        companion_id = request.GET.get('companion_id')
        companion = Companion.objects.filter(id=companion_id).first()
        tag_set = TagOnCompanion.objects.filter(companion=companion)
        tag_val_set = []
        for tagOnTravel in tag_set:
            if tagOnTravel.tag.forbidden == 0:
                tag_val_set.append(tagOnTravel)
        tag_ser = TagOnCompanionSerializer(tag_set, many=True)
        return Response(tag_ser.data, status=status.HTTP_200_OK)
        
    @action(methods=['GET'], detail=False, url_path='getTagList')
    def getTagList(self, request, *args, **kwargs):
        forbidden = 0
        tags = Tag.objects.filter(forbidden=forbidden)
        tags_ser = TagSerializer(tags,many = True)
        return Response(tags_ser.data, status=status.HTTP_200_OK)