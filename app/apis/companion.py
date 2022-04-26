from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied, NotFound
from rest_framework.decorators import action
from django.http import QueryDict
from django.db.models import Sum, F, Count, Q

from app.response import *
from django.conf import settings
from app.models import Companion, Message, Comment
from app.serializers import CompanionSerializer, CommentSerializer
from app.utilities import permission
from . import PositionApis
from utilities import permission as _permission, filters, conversion, date


class CompanionFilterBackend(filters.QueryFilterBackend):
    filter_fields = [
        ('id', 'id', 'exact'),
        ('owner', 'owner_id', 'exact'),
        ('position', 'position.position.id', 'exact'),
        ('fellow', 'fellows.id', 'exact'),
        ('forbidden', 'forbidden'),
    ]
    default_ordering_rule = '-time'

    def filter_queryset(self, request, queryset, view):
        owner = _permission.user_check(request)
        if owner >= 0:
            queryset = super().filter_queryset(request, queryset.filter(Q(forbidden=settings.TRAVEL_FORBIDDEN_FALSE) |
                                                                        Q(owner_id=owner)), view)
        query_content = request.query_params.get('content', None)
        if query_content:
            queryset = queryset.filter(Q(title__contains=query_content) | \
                       Q(owner__name__contains=query_content))
        query_status = conversion.get_int(request.query_params, 'status')
        date_now = date.now()
        if query_status == settings.COMPANION_STATUS_RECRUITING:
            queryset = queryset.filter(deadline__gt=date_now)
        elif query_status == settings.COMPANION_STATUS_END_RECRUIT:
            queryset = queryset.filter(Q(deadline__lte=date_now) & Q(start_time__gt=date_now))
        elif query_status == settings.COMPANION_STATUS_STARTED:
            queryset = queryset.filter(Q(start_time__lte=date_now) & Q(end_time__gt=date_now))
        elif query_status == settings.COMPANION_STATUS_ENDED:
            queryset = queryset.filter(end_time__lte=date_now)
        queryset = super().filter_queryset(request, queryset, view)
        return queryset


class CompanionApis(viewsets.ModelViewSet):
    filter_backends = [CompanionFilterBackend]
    permission_classes = [permission.ContentPermission]
    queryset = Companion.objects.all()
    serializer_class = CompanionSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        now = date.now()
        print(now)
        if now > obj.time + date.delta(settings.COMPANION_REMOVABLE_TIME):
            return error_response(Error.COMPANION_CANNOT_REMOVE, "Cannot remove companion", status=403)
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        data['owner'] = request_user
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        private_content = request.data.get('private_content', None)
        if private_content is not None:
            obj.private_content = private_content
            obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        request_user = _permission.user_check(request)
        if obj.owner_id != request_user and obj.forbidden != settings.TRAVEL_FORBIDDEN_FALSE:
            return NotFound()
        serializer = self.get_serializer_class()(obj, context=self.get_serializer_context())
        data = serializer.data
        joined = request_user == obj.owner_id or not not obj.fellows.filter(id=request_user)
        data['joined'] = joined
        if request_user < 0 or joined:
            data['private_content'] = obj.private_content
            data['comments'] = obj.comments.values_list('id', flat=True)
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        private_content = request.data.get('private_content', None)
        instance = self.get_object()
        if private_content is not None:
            instance.private_content = private_content
            instance.save()
        res.data['private_content'] = instance.private_content
        return res

    @permission.whiteaction(methods=['GET', 'POST'], detail=True, url_path='comments')
    def comments(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        obj = self.get_object()
        is_owner = obj.owner_id == request_user
        if obj.forbidden and not is_owner:
            raise NotFound()
        if request.method == 'POST':
            return self.comment_create(request, *args, **kwargs)
        return self.comment_retrieve(request, *args, **kwargs)

    def comment_retrieve(self, request, *args, **kwargs):
        direct = conversion.get_bool(request.GET, 'direct')
        if direct:
            queryset = Comment.objects.filter(companion_master=self.get_object(), deleted=False, reply=None)
        else:
            queryset = Comment.objects.filter(companion_master=self.get_object(), deleted=False)

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
        data['type'] = settings.COMMENT_TYPE_COMPANION
        serializer = CommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        obj = self.get_object()
        comment.companion_master = obj
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
                Message.create_message(comment.owner, comment.reply.owner, settings.MESSAGE_TYPE_COMMENT_ON_COMMENT, comment=comment.reply)
        else:
            if owner_id != obj.owner_id:
                Message.create_message(comment.owner, obj.owner, settings.MESSAGE_TYPE_COMMENT_ON_TRAVEL, companion=obj)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['GET'], detail=False, url_path='recommend')
    def recommend(self, request, *args, **kwargs):
        count = conversion.get_int(request.query_params, 'count')
        if count is None:
            count = settings.POSITION_RECOMMEND_AMOUNT
        else:
            count = min(count, settings.POSITION_RECOMMEND_MAX_AMOUNT)
        pos = PositionApis.recommend_positions(request, amount=count)

        queryset = filters.random_filter(self.get_queryset().filter(position__position__id__in=pos), count)
        if queryset.count() < count:
            ids = queryset.values_list('id', flat=True)
            queryset |= self.get_queryset().exclude(id__in=ids)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(data={'count': len(data), 'data': data})
