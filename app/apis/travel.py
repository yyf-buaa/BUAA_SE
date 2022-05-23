from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied, NotFound
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, F, Count, Q
from django.http import QueryDict
import random

from django.conf import settings
from app.models import Travel, AppUser, Image, Address, Comment, Message
from app.models.travel import ReadRecord
from app.serializers import TravelSerializer, TravelAddressSerializer, AddressSerializer, CommentSerializer
from app.utilities import permission
from app.response import *
from utilities import conversion, permission as _permission, filters
from django.core.files.uploadedfile import UploadedFile
from recommend.recInterface import getUserLike, getKNNitem


class TravelFilterBackend(filters.QueryFilterBackend):
    filter_fields = [
        ("owner", "owner_id", "exact"),
        ("owner_name", "owner__name", "contains"),
        ("title", "title", "contains"),
    ]
    default_ordering_rule = '-time'

    def filter_queryset(self, request, queryset, view):
        owner = _permission.user_check(request)
        queryset = super().filter_queryset(request, queryset.filter(Q(forbidden=settings.TRAVEL_FORBIDDEN_FALSE,
                                                                      visibility=settings.TRAVEL_VISIBILITIES_ALL) |
                                                                    Q(owner_id=owner)), view)
        position = request.query_params.get('position', None)
        if position is not None:
            if position[-4:] == '0000':
                queryset = queryset.filter(position__province_position_id=position)
            elif position[-2:] == '00':
                queryset = queryset.filter(position__city_position_id=position)
            else:
                queryset = queryset.filter(position__position_id=position)
        if view:
            action = view.action
            if action != 'list':
                return queryset
        order = conversion.get_int(request.query_params, 'order')
        if not order in settings.TRAVEL_LIST_MODES:
            order = settings.TRAVEL_LIST_MODE_DEFAULT
        if order == settings.TRAVEL_LIST_MODE_TIME:
            queryset = queryset.order_by('-time')
        elif order == settings.TRAVEL_LIST_MODE_HEAT:
            queryset = self.heat_annotate(queryset)
        elif order == settings.TRAVEL_LIST_MODE_RECOMMEND:
            queryset = queryset
        return queryset

    @classmethod
    def heat_annotate(cls, queryset):
        return queryset \
            .annotate(heat= \
                          settings.TRAVEL_HEAT_WEIGHT_RECENT * Sum('read_records__amount') + \
                          settings.TRAVEL_HEAT_WEIGHT_COLLECTIONS * Count('collectors') + \
                          settings.TRAVEL_HEAT_WEIGHT_LIKES * Count('likes') + \
                          settings.TRAVEL_HEAT_WEIGHT_COMMENTS * Count('comments')
                      ) \
            .order_by('-heat')


class TravelApis(viewsets.ModelViewSet):
    permission_classes = [permission.ContentPermission]
    filter_backends = [TravelFilterBackend, DjangoFilterBackend]
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        request_user = _permission.user_check(request)
        is_owner = obj.owner_id == request_user
        if (obj.forbidden or obj.visibility == settings.TRAVEL_VISIBILITIES_PRIVATE) and not is_owner:
            raise NotFound()

        obj.read_increase()
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        data = serializer.data
        if request_user > 0:
            data['liked'] = True if obj.likes.filter(id=request_user) else False
        else:
            data['liked'] = False
        if is_owner:
            data['forbidden_reason'] = obj.forbidden_reason
        return Response(data)

    @action(methods=["GET"], detail=False, url_path='positions')
    def list_positions(self, request, *args, **kwargs):
        """
        owner = _permission.user_check(request)
        if owner <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        #"""
        owner = conversion.get_int(request.GET, 'id', errtype=ParseError)
        queryset = self.filter_queryset(self.get_queryset().filter(owner_id=owner))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TravelAddressSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TravelAddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        owner = _permission.user_check(request)
        if owner <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        if 'position' in data:
            position = data.get('position')
        else:
            position = None
        data['owner'] = owner
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        if position:
            obj.position = Address.create_address(position)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception as e:
            print(e)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @permission.whiteaction(methods=['POST'], detail=True, url_path='like')
    def like(self, request, *args, **kwargs):
        owner = _permission.user_check(request)
        if owner <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        if not AppUser.objects.filter(id=owner):
            return error_response(Error.INVALID_USER, 'Invalid user.', status=status.HTTP_400_BAD_REQUEST)
        obj = self.get_object()
        cancel = conversion.get_bool(request.data, 'cancel')
        if cancel:
            obj.likes.remove(owner)
            msg = Message.objects.filter(related_travel=obj, owner=owner, type=settings.MESSAGE_TYPE_LIKE_TRAVEL)
            if msg:
                msg.delete()
        else:
            obj.likes.add(owner)
            if not Message.objects.filter(related_travel=obj, owner=owner, type=settings.MESSAGE_TYPE_LIKE_TRAVEL):
                Message.create_message(owner, obj.owner, settings.MESSAGE_TYPE_LIKE_TRAVEL, travel=obj)
        return response()

    @action(methods=['GET'], detail=False, url_path='newRecommend')
    def newRecommend(self, request, *args, **kwargs):
        owner_id = _permission.user_check(request)
        user = AppUser.objects.filter(id=owner_id)
        if user:
            try:
                travel_list = getUserLike(owner_id)
                travels = Travel.objects.filter(id__in=travel_list)
                travels = dict([(obj.id, obj) for obj in travels]) 
                sotedTravels = []
                for id in travel_list:
                    if id not in travels.keys():
                        continue
                    sotedTravels.append(travels[id])
                
                serializer = self.get_serializer(sotedTravels, many=True)
                data = serializer.data
                for d, obj in zip(data, sotedTravels):
                    if user:
                        d['liked'] = True if obj.likes.filter(id=owner_id) else False
                    else:
                        d['liked'] = False
                return Response({'count': len(data), 'data': data}, status=status.HTTP_200_OK)
            except:
                travels = Travel.objects.all()
                data = self.get_list_data(request, travels)
                return Response({'count': len(data), 'data': data}, status=status.HTTP_200_OK)

        travels = Travel.objects.all()
        data = self.get_list_data(request, travels)
        return Response({'count': len(data), 'data': data}, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='image')
    def image(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            return self.image_delete(request, *args, **kwargs)
        return self.image_upload(request, *args, **kwargs)

    def image_upload(self, request, *args, **kwargs):
        obj = self.get_object()
        imgfile = request.data.get('image', None)
        if imgfile is None or not isinstance(imgfile, UploadedFile):
            return error_response(status.HTTP_400_BAD_REQUEST, 'Invalid image.', status=status.HTTP_400_BAD_REQUEST)
        desc = request.data.get('description', '')
        image = Image.objects.create(image=imgfile, description=desc)
        obj.images.add(image)
        return response({'id': image.id})

    def image_delete(self, request, *args, **kwargs):
        obj = self.get_object()
        imgid = conversion.get_list(request.data, 'id')
        images = obj.images.filter(id__in=imgid)
        images.delete()
        return response()

    @action(methods=['POST', 'DELETE'], detail=True, url_path='cover')
    def cover(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            return self.cover_delete(request, *args, **kwargs)
        return self.cover_upload(request, *args, **kwargs)

    def cover_upload(self, request, *args, **kwargs):
        obj = self.get_object()
        imgfile = request.data.get('image', None)
        if imgfile is None or not isinstance(imgfile, UploadedFile):
            return error_response(status.HTTP_400_BAD_REQUEST, 'Invalid image.', status=status.HTTP_400_BAD_REQUEST)
        desc = request.data.get('description', '')
        image = Image.objects.create(image=imgfile, description=desc)
        obj.cover = image
        obj.save()
        return response({'id': image.id})

    def cover_delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.cover = None
        obj.save()
        return response()

    @permission.whiteaction(methods=['GET', 'POST'], detail=True, url_path='comments')
    def comments(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        obj = self.get_object()
        is_owner = obj.owner_id == request_user
        if (obj.forbidden or obj.visibility == settings.TRAVEL_VISIBILITIES_PRIVATE) and not is_owner:
            raise NotFound()
        if request.method == 'POST':
            return self.comment_create(request, *args, **kwargs)
        return self.comment_retrieve(request, *args, **kwargs)

    def comment_retrieve(self, request, *args, **kwargs):
        direct = conversion.get_bool(request.GET, 'direct')
        if direct:
            queryset = Comment.objects.filter(
                master=self.get_object(),
                reply=None,
                # deleted=False,
            )
        else:
            queryset = Comment.objects.filter(
                master=self.get_object(),
                # deleted=False,
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def comment_create(self, request, *args, **kwargs):
        owner_id = _permission.user_check(request)
        if owner_id <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        data['owner'] = owner_id
        data['type'] = settings.COMMENT_TYPE_TRAVEL

        serializer = CommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        obj = self.get_object()
        comment.master = obj
        comment.save()

        reply = comment.reply
        if reply:
            root = reply.reply_root
            if root:
                comment.reply_root = root
            else:
                comment.reply_root = reply
            comment.save()

        if comment.reply:
            if owner_id != comment.reply.owner_id:
                Message.create_message(comment.owner, comment.reply.owner, settings.MESSAGE_TYPE_COMMENT_ON_COMMENT,
                                       comment=comment.reply)
        else:
            if owner_id != obj.owner_id:
                Message.create_message(comment.owner, obj.owner, settings.MESSAGE_TYPE_COMMENT_ON_TRAVEL, travel=obj)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['GET'], detail=False, url_path='recommend')
    def recommend(self, request: Request, *args, **kwargs):
        owner_id = _permission.user_check(request)
        if owner_id > 0:
            user = AppUser.objects.filter(id=owner_id)
            if user:
                user = user.first()
            else:
                user = None
        else:
            user = None
        amount = conversion.get_int(request.query_params, 'count')
        if amount is None:
            amount = settings.TRAVEL_RECOMMEND_DEFAULT_AMOUNT
        else:
            amount = min(amount, settings.TRAVEL_RECOMMEND_MAX_AMOUNT)

        self_queryset = self.get_queryset().filter(Q(forbidden=settings.TRAVEL_FORBIDDEN_FALSE,
                                                     visibility=settings.TRAVEL_VISIBILITIES_ALL))

        if user is not None:
            filter_args = {}

            first_likes = user.first_likes()
            if first_likes:
                filter_args['time__gte'] = first_likes[first_likes.count() - 1].time
            liked_users = first_likes.values_list('owner_id', flat=True)

            cluster_amount = round(
                settings.TRAVEL_RECOMMEND_CLUSTER_WEIGHT * amount * settings.TRAVEL_RECOMMEND_EXCEED_RATE)
            user_amount = round(settings.TRAVEL_RECOMMEND_USER_WEIGHT * amount * settings.TRAVEL_RECOMMEND_EXCEED_RATE)
            heat_amount = round(settings.TRAVEL_RECOMMEND_HEAT_WEIGHT * amount * settings.TRAVEL_RECOMMEND_EXCEED_RATE)

            cluster_query = self_queryset.filter(likes__cluster=user.cluster, **filter_args)
            cluster_query = filters.random_filter(cluster_query, cluster_amount).distinct()
            cluster_ids = cluster_query.values_list('id', flat=True)
            user_query = self_queryset.exclude(id__in=cluster_ids).filter(owner_id__in=liked_users, **filter_args)
            user_amount += max(0, cluster_amount - cluster_query.count())
            user_query = filters.random_filter(user_query, user_amount).distinct()
            user_ids = user_query.values_list('id', flat=True)
            heat_query = TravelFilterBackend.heat_annotate(self_queryset.exclude(id__in=user_ids | cluster_ids))

            heat_amount += max(0, user_amount - user_query.count())

            data = cluster_query | user_query
            a = round((settings.TRAVEL_RECOMMEND_CLUSTER_WEIGHT + settings.TRAVEL_RECOMMEND_USER_WEIGHT) * amount)
            data = filters.random_filter(data, a, distinct=True)
            data = self.get_list_data(request, data)
            data1 = [q for q in heat_query[:heat_amount]]
            data1 = random.sample(data1, min(amount - a, len(data1)))
            data += self.get_list_data(request, data1)
        else:
            data = self_queryset
            data = filters.random_filter(data, amount, distinct=True)
            data = self.get_list_data(request, data)
        filters.shuffle(data)
        return Response({'count': len(data), 'data': data})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            data = self.get_list_data(request, page)
            return self.get_paginated_response(data)

        data = self.get_list_data(request, queryset)
        return Response(data)

    def get_list_data(self, request, queryset):
        owner_id = _permission.user_check(request)
        if owner_id > 0:
            user = AppUser.objects.filter(id=owner_id)
            if user:
                user = user.first()
            else:
                user = None
        else:
            user = None
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for d, obj in zip(data, queryset):
            if user:
                d['liked'] = True if obj.likes.filter(id=owner_id) else False
            else:
                d['liked'] = False
        return data

    @action(methods=['GET'], detail=True, url_path='similar')
    def similar(self, request, *args, **kwargs):
        obj: Travel = self.get_object()
        count = conversion.get_int(request.query_params, 'count')
        if count is None:
            count = settings.TRAVEL_SIMILAR_AMOUNT
        else:
            count = min(count, settings.TRAVEL_SIMILAR_MAX_AMOUNT)

        self_queryset = self.get_queryset().filter(Q(forbidden=settings.TRAVEL_FORBIDDEN_FALSE,
                                                     visibility=settings.TRAVEL_VISIBILITIES_ALL))

        queryset = self_queryset.exclude(id=obj.id)
        if obj.position is None:
            data = self.get_list_data(request, filters.random_filter(queryset, count))
        else:
            same_district = queryset.filter(position__position__id=obj.position.position_id)
            c = count - same_district.count()
            if c > 0:
                same_city = queryset.filter(position__city_position__id=obj.position.city_position_id)
                c1 = c - same_city.count()
                if c1 > 0:
                    same_province = queryset.filter(position__province_position__id=obj.position.province_position_id)
                    ids = same_city.values_list('id', flat=True)
                    same_province = same_province.exclude(id__in=ids)
                    same_province = filters.random_filter(same_province, c1)
                    same_province = same_province.exclude(id__in=same_city.values_list('id', flat=True))
                    if same_province:
                        same_city |= same_province
                else:
                    ids = same_district.values_list('id', flat=True)
                    same_city = same_city.exclude(id__in=ids)
                    same_city = filters.random_filter(same_city, c)
                same_city = same_city.exclude(id__in=same_district.values_list('id', flat=True))
                if same_city:
                    same_district = list(same_city) + list(same_district)
                else:
                    same_district = list(same_district)
            else:
                same_district = filters.random_filter(same_district, count)
                same_district = list(same_district)

            c = count - len(same_district)
            if c > 0:
                ids = list(map(lambda x: x.id, same_district))  # same_district.values_list('id', flat=True)
                queryset = queryset.exclude(id__in=ids)
                same_district += list(filters.random_filter(queryset, c))

            data = self.get_list_data(request, same_district)
        filters.shuffle(data)
        return Response({'count': len(data), 'data': data})
