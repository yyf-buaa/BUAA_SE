from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied
from rest_framework.decorators import action

from django.conf import settings
from app.models import Position, AppUser, Travel,BlackPos, Plan, Companion, Comment,Flight
from app.serializers import PositionSerializer,BlackPosSerializer
from app.response import *
from main.constants import *
from utilities.location import nearest
from utilities import conversion, permission as _permission, filters


class PositionFilterBackend(filters.QueryFilterBackend):
    filter_fields = [
        ('name', 'name', 'contains'),
        ('id', 'id', 'contains'),
    ]
    default_ordering_rule = 'id'

    def filter_queryset(self, request, queryset, view):
        return super().filter_queryset(request, queryset.exclude(visibility=False), view)

class PositionApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin):
    filter_backends = [PositionFilterBackend]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    serializer_blackPos = BlackPosSerializer


    @action(methods=['GET'], detail=False, url_path='subarea')
    def subarea(self, request, *args, **kwargs):

        adcode = request.GET.get('adcode', None)
        if adcode is None:
            return error_response(400)
        subs = settings.ADCODE.get(adcode, None)
        if subs is None:
            return error_response(400)
        children = []
        for c in subs['children']:
            c = settings.ADCODE.get(c, None)
            if c is None: continue
            c = {'name': c['name'], 'longitude': c['longitude'], 'latitude': c['latitude']}
            children.append(c)
        return response(children)

    @action(methods=['GET'], detail=False, url_path='location')
    def location(self, request, *args, **kwargs):
        lon = conversion.get_float(request.GET, 'longitude')
        lat = conversion.get_float(request.GET, 'latitude')
        if lon is None or lat is None:
            return error_response(400)
        adcode, name, lon, lat = nearest(lon, lat)
        return response({'adcode': adcode, 'name': name, 'longitude': lon, 'latitude': lat})
        
    @action(methods=['GET'], detail=False, url_path='trafficPositions')
    def trafficPositions(self, request, *args, **kwargs):
        positions = Position.objects.filter(name__endswith='市')
        position = self.serializer_class(positions, many=True)
        return Response(position.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='hot')
    def hot_positions(self, request, *args, **kwargs):
        positions = Position.objects.filter(id__endswith='00')
        positions = positions.exclude(id__endswith='0000')
        addp = Position.objects.filter(id__endswith='0000', name__endswith='市')
        positions = positions | addp
        for position in positions:
            heat = 10
            # 本地点游记
            travels = Travel.objects.filter(owner__position__city_position=position)
            heat += travels.count() * FACTOR_TRAVEL_CREATE_GLOBAL
            # 游记点赞数he阅读数
            for travel in travels:
                heat += travel.read_total * FACTOR_TRAVEL_READ_GLOBAL + travel.likes.count() *FACTOR_TRAVEL_LIKE_GLOBAL
            # 计划出行数
            # plans = Plan.objects.filter(position=position)
            # heat += plans.count() * FACTOR_PLAN_GLOBAL
            # 同行活动
            companions = Companion.objects.filter(owner__position__city_position=position)
            heat += companions.count() * FACTOR_COMPANION_CREATE_GLOBAL
            for companion in companions:
                heat += companion.fellows.count() * FACTOR_COMPANION_PARTICIPATE_GLOBAL
            # 航班数
            flights = Flight.objects.filter(endcity=position.name[:-1])
            heat += flights.count() * FACTOR_FLIGHT
            setattr(position, 'heat', heat)
            position.save()
        owner_id = _permission.user_check(request)
        user = AppUser.objects.filter(id=owner_id)
        if user:
            user = user.first()
            blackp = BlackPos.objects.filter(person=user, type='黑名单', position__in=positions)
            collectp = BlackPos.objects.filter(person=user, type='收藏', position__in=positions)
            for collect in collectp:
                heat0 = collect.position.heat * 10
                setattr(collect.position, 'heat', heat0)
                collect.position.save()
            for black in blackp:
                positions = positions.exclude(id=black.position_id)
        hot = positions.order_by('-heat')
        hot = self.serializer_class(hot, many=True)
        return Response(data={'count': positions.count(), 'pages': positions.count()//20 + 1, "next": "", 'previous': "",
                              'result':hot.data}, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='recommend')
    def recommend(self, request, *args, **kwargs):
        count = conversion.get_int(request.query_params, 'count')
        if count is None:
            count = settings.POSITION_RECOMMEND_AMOUNT
        else:
            count = min(count, settings.POSITION_RECOMMEND_MAX_AMOUNT)
        pos = self.recommend_positions(request, amount=count, unique=True)
        queryset = self.get_queryset().filter(id__in=pos)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(data={'count': len(data), 'data': data})
      
    @classmethod
    def recommend_positions(cls, request, amount=3, unique=False):
        owner_id = _permission.user_check(request)
        if owner_id <= 0:
            return filters.random_filter(Position.objects.all(), amount).values_list('id', flat=True)
        user = AppUser.objects.filter(id=owner_id)
        if not user:
            return filters.random_filter(Position.objects.all(), amount).values_list('id', flat=True)
        user = user.first()

        filter_args = {}

        first_likes = user.first_likes()
        if first_likes:
            filter_args['time__gte'] = first_likes[first_likes.count() - 1].time

        likes = Travel.objects.filter(likes__cluster=user.cluster, position__position__isnull=False, **filter_args)
        if unique:
            positions = filters.random_filter(likes, amount * settings.POSITION_RECOMMEND_TRUNCATE).values_list('position__position__id', flat=True).distinct()[:amount]
        else:
            positions = filters.random_filter(likes, amount).values_list('position__position__id', flat=True)
        positions = list(positions)
        if len(positions) < amount:
            positions += list(filters.random_filter(Position.objects.exclude(id__in=positions), amount - len(positions)).values_list('id', flat=True))
        return positions
