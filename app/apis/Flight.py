from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied
from rest_framework.decorators import action

from app.models import Flight, FlightPriceList, AppUser, Position, Address, BlackPos, AppUser, Position,Travel, Companion
from app.serializers import FlightSerializer, FlightPriceListSerializer, PositionSerializer
from app.utilities import permission
from app.response import *
from utilities import conversion, filters, permission as _permission
import pandas
import datetime
from main.constants import *


class FlightApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
                 viewsets.mixins.RetrieveModelMixin):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    queryset_price = FlightPriceList.objects.all()
    serializer_class_price = FlightPriceListSerializer

    # 传入flight_id返回航班的详细信息
    @action(methods=['GET'], detail=False, url_path='getFlightInfo')
    def getFlightInfo(self, request, *args, **kwargs):
        flight_id = request.GET.get('flightid')
        flight = Flight.objects.filter(id=flight_id)
        serializer_flight = self.serializer_class(flight, many=True)
        return Response(serializer_flight.data, status=status.HTTP_200_OK)

    # 传入航班表的id返回这趟航班对应的价格表
    @action(methods=['GET'], detail=False, url_path='getPriceList')
    def getPriceList(self, request, *args, **kwargs):
        id = request.GET.get('id')
        priceList = FlightPriceList.objects.filter(owner_id=id)
        serializer_price = self.serializer_class_price(priceList, many=True)
        return Response(serializer_price.data, status=status.HTTP_200_OK)

    # 传入'航班号,出发地,目的地'获取航班详细信息
    @action(methods=['GET'], detail=False, url_path='getFlightNo')
    def getFlightNo(self, request, *args, **kwargs):
        flight_no = request.GET.get('flightno')
        departure = request.GET.get('departure')
        arrival = request.GET.get('arrival')
        departdate = request.GET.get('departdate')
        # 查询航班号的信息 至 列表flight_list
        flight = Flight.objects.filter(flightno=flight_no)
        flight_list = self.serializer_class(flight, many=True)
        # 返回符合出发地-目的地的航班信息
        for i in flight_list.data:
            if i['city'] == departure and i['endcity'] == arrival and departdate == i['departdate']:
                i['departtime'] = i['departtime'][:-3]
                i['arrivaltime'] = i['arrivaltime'][:-3]
                i['departport'] = i['departport'] + ' ' + i['departterminal']
                i['arrivalport'] = i['arrivalport'] + ' ' + i['arrivalterminal']
                #                date1 = pandas.to_datetime(i['departdate'], format='%Y-%m-%d')
                #                date2 = pandas.to_datetime(i['arrivaldate'], format='%Y-%m-%d')
                #                nowdate = pandas.to_datetime(departdate, format='%Y-%m-%d')
                #                interval1 = nowdate - date1
                #                i['departdate'] = (date1 + datetime.timedelta(days=+interval1.days)).strftime("%Y-%m-%d")
                #                i['arrivaldate'] = (date2 + datetime.timedelta(days=+interval1.days)).strftime("%Y-%m-%d")
                return Response(i)
        return Response(status=status.HTTP_400_BAD_REQUEST)
   
    # 热门地点廉航推荐
    @action(methods=['GET'], detail=False, url_path='getHCFlight')
    def getHCFlight(self, request, *args, **kwargs):
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
                heat += travel.read_total * FACTOR_TRAVEL_READ_GLOBAL + travel.likes.count() * FACTOR_TRAVEL_LIKE_GLOBAL
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
        if owner_id <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        user = AppUser.objects.filter(id=owner_id).first()
        try:
            departure = user.position.city
        except:
            return error_response(Error.NOT_LOGIN, 'Please 完善信息.', status=status.HTTP_400_BAD_REQUEST)
        blackp = BlackPos.objects.filter(person=user)
        for black in blackp:
            positions = positions.exclude(id=black.position_id)
        hot = positions.order_by('-heat')[0]
        arrival = hot.name
        date = (datetime.datetime.now() + datetime.timedelta(days=+1)).date()
        flight = Flight.objects.filter(city=departure[:-1], endcity=arrival[:-1], departdate=date)
        for f in flight:
            prices = FlightPriceList.objects.filter(owner=f, price__gt=0).order_by('price')
            if len(prices) > 0:
                setattr(f, 'minprice', prices[0].price)
                f.save()
        flight = flight.exclude(minprice=0)
        flight = flight.order_by('minprice')
        serializer_flight = self.serializer_class(flight, many=True)
        return Response(serializer_flight.data, status=status.HTTP_200_OK)

    # 地点廉航推荐
    @action(methods=['GET'], detail=False, url_path='getCheapFlight')
    def getCheapFlight(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        try:
            departure = AppUser.objects.filter(id=request_user).first().position.city
        except:
            return error_response(Error.NOT_LOGIN, 'Please 完善信息.', status=status.HTTP_400_BAD_REQUEST)
        arrival = request.GET.get('position')
        date = (datetime.datetime.now() + datetime.timedelta(days=+1)).date()
        flight = Flight.objects.filter(city=departure[:-1], endcity=arrival, departdate=date)
        for f in flight:
            prices = FlightPriceList.objects.filter(owner=f, price__gt=0).order_by('price')
            if len(prices) > 0:
                setattr(f, 'minprice', prices[0].price)
                f.save()
        flight = flight.exclude(minprice=0)
        flight = flight.order_by('minprice')
        serializer_flight = self.serializer_class(flight, many=True)
        return Response(serializer_flight.data, status=status.HTTP_200_OK)

    # 直达航班查询
    @action(methods=['GET'], detail=False, url_path='getThroughFlight')
    def getThroughFlight(self, request, *args, **kwargs):
        departure = request.GET.get('departure')
        arrival = request.GET.get('arrival')
        date = request.GET.get('date')
        flight_set = Flight.objects.filter(city__icontains=departure, endcity__icontains=arrival, departdate=date)
        return Response(self.serializer_class(flight_set, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='addblackPos')
    def addblackPos(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        position = request.data.get('position')
        blackPos = BlackPos()
        blackPos.person = AppUser.objects.filter(id=request_user).first()
        blackPos.position = Position.objects.filter(id=position).first()
        blackPos.type = '黑名单'
        blackPos.save()
        return Response(True, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='addToFavorites')
    def addToFavorites(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        position = request.data.get('position')
        blackPos = BlackPos()
        blackPos.person = AppUser.objects.filter(id=request_user).first()
        blackPos.position = Position.objects.filter(id=position).first()
        blackPos.type = '收藏'
        blackPos.save()
        return Response(True, status=status.HTTP_200_OK)


    @action(methods=['GET'], detail=False, url_path='getMyBlackPos')
    def getMyBlackPos(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        blackPos_set = BlackPos.objects.filter(person=request_user, type='黑名单')
        position_list = []
        for blackPos in blackPos_set:
            position_list.append(blackPos.position)
        return Response(PositionSerializer(position_list, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='getMyFav')
    def getMyFavorites(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        blackPos_set = BlackPos.objects.filter(person=request_user, type='收藏')
        position_list = []
        for blackPos in blackPos_set:
            position_list.append(blackPos.position)
        return Response(PositionSerializer(position_list, many=True).data, status=status.HTTP_200_OK)
    @action(methods=['POST'], detail=False, url_path='isMyBlackPos')
    def isMyBlackPos(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        position = request.data.get('position')
        blackPos_set = BlackPos.objects.filter(person=request_user, type='黑名单',position = position)
        position_list = []
        if len(blackPos_set)>0:
            return Response(True, status=status.HTTP_200_OK)
        else:
            return Response(False, status=status.HTTP_200_OK)


    @action(methods=['POST'], detail=False, url_path='isMyFavorites')
    def isMyFavorites(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        position = request.data.get('position')
        blackPos_set = BlackPos.objects.filter(person=request_user, type='收藏',position = position)
        position_list = []
        if len(blackPos_set)>0:
            return Response(True, status=status.HTTP_200_OK)
        else:
            return Response(False, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='deleteMyBlackPos')
    def deleteMyBlackPos(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        position = request.data.get('position')
        blackPos_set = BlackPos.objects.filter(person=request_user, type='黑名单',position = position)
        blackPos_set.delete()
        return Response(True, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='deleteMyFavorites')
    def deleteMyFavorites(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        position = request.data.get('position')
        blackPos_set = BlackPos.objects.filter(person=request_user, type='收藏',position = position)
        blackPos_set.delete()
        return Response(True, status=status.HTTP_200_OK)