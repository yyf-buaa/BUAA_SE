from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied
from rest_framework.decorators import action

from app.models import Train, TrainPriceList, AppUser, Position, FlightPriceList, Flight, Transfer
from app.serializers import TrainSerializer, TrainPriceListSerializer, TransferSerializer, PriceTrainListSerializer
import datetime

from django.db.models import QuerySet
from app.utilities import permission
from app.response import *
from utilities import conversion, filters, permission as _permission


class TrainApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
                viewsets.mixins.RetrieveModelMixin):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    queryset_price = TrainPriceList.objects.all()
    serializer_class_price = TrainPriceListSerializer
    serializer_class_transfer = TransferSerializer

    # 传入id返回列车的详细信息
    @action(methods=['GET'], detail=False, url_path='getTrainInfo')
    def getTrainInfo(self, request, *args, **kwargs):
        train_id = request.GET.get('id')
        train = Train.objects.filter(id=train_id)
        serializer_flight = self.serializer_class(train, many=True)
        return Response(serializer_flight.data, status=status.HTTP_200_OK)

    # 地点廉火车推荐
    @action(methods=['GET'], detail=False, url_path='getCheapTrain')
    def getCheapTrain(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        try:
            departure = AppUser.objects.filter(id=request_user).first().position.city
        except:
            return error_response(Error.NOT_LOGIN, 'Please 完善信息.', status=status.HTTP_400_BAD_REQUEST)
        if departure == '':
            return error_response(Error.NOT_LOGIN, 'Please 完善信息.', status=status.HTTP_400_BAD_REQUEST)
        arrival = request.GET.get('position')
        date = datetime.datetime.now()
        trains = Train.objects.filter(station__icontains=departure[:-1], endstation__icontains=arrival,
                                      departdate=date.date(), departtime__gt=date.time())
        priceList = TrainPriceList.objects.filter(owner_id=0)
        for train in trains:
            prices = TrainPriceList.objects.filter(owner=train)
            if len(prices):
                prices = prices.order_by('price')[:1]
            priceList = priceList | prices
        priceList = priceList.order_by('price')
        serializer_train = PriceTrainListSerializer(priceList, many=True)
        return Response(serializer_train.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='getTransfer')
    def getTransfer(self, request, *args, **kwargs):
        departure = request.GET.get('departure')
        arrival = request.GET.get('arrival')
        date = request.GET.get('date')
        # 飞机+飞机
        min_price = 999999999;
        transfer1 = Transfer()
        flight1_set = Flight.objects.filter(city=departure, departdate=date).exclude(endcity=arrival)
        train1_set = Train.objects.filter(station__icontains=departure, departdate=date).exclude(endstation__icontains=arrival)
        for flight1 in flight1_set:
            arrival1 = flight1.endcity
            date1 = flight1.arrivaldate
            time1 = flight1.arrivaltime
            flight2_set = Flight.objects.filter(city=arrival1, endcity=arrival, departdate=date1, departtime__gte=time1)
            for flight2 in flight2_set:
                total_price = flight1.minprice + flight2.minprice
                if total_price < min_price and flight1.flightno!=flight2.flightno:
                    min_price = total_price
                    transfer1.id1 = flight1.id
                    transfer1.type1 = '飞机'
                    transfer1.id2 = flight2.id
                    transfer1.type2 = '飞机'

        # 火车+火车
        min_price = 999999999;
        transfer2 = Transfer()
        for train1 in train1_set:
            train1_price_set = TrainPriceList.objects.filter(owner=train1.id)
            train1_price = 999999999
            for train1_price_temp in train1_price_set:
                if train1_price_temp.price < train1_price:
                    train1_price = train1_price_temp.price
            arrival1 = train1.endstation
            date1 = train1.arrivaldate
            time1 = train1.arrivaltime
            train2_set = Train.objects.filter(station=arrival1, endstation__icontains=arrival, departdate=date1,
                                              departtime__gte=time1)
            train2_price = 999999999
            for train2 in train2_set:
                train2_price_set = TrainPriceList.objects.filter(owner=train2.id)
                for train2_price_temp in train2_price_set:
                    if train2_price_temp.price < train2_price:
                        train2_price = train2_price_temp.price
                total_price = train1_price + train2_price
                if total_price < min_price and train1.trainno != train2.trainno:
                    min_price = total_price
                    transfer2.id1 = train1.id
                    transfer2.type1 = '火车'
                    transfer2.id2 = train2.id
                    transfer2.type2 = '火车'
        # 飞机+火车
        min_price = 999999999;
        transfer3 = Transfer()
        for flight1 in flight1_set:
            arrival1 = flight1.endcity
            date1 = flight1.arrivaldate
            time1 = flight1.arrivaltime
            train2_set = Train.objects.filter(station__icontains=arrival1, endstation__icontains=arrival,
                                              departdate=date1, departtime__gte=time1)
            train2_price = 999999999
            for train2 in train2_set:
                train2_price_set = TrainPriceList.objects.filter(owner=train2.id)
                for train2_price_temp in train2_price_set:
                    if train2_price_temp.price < train2_price:
                        train2_price = train2_price_temp.price
                total_price = flight1.minprice + train2_price
                if total_price < min_price:
                    min_price = total_price
                    transfer3.id1 = flight1.id
                    transfer3.type1 = '飞机'
                    transfer3.id2 = train2.id
                    transfer3.type2 = '火车'

        # 火车+飞机
        min_price = 999999999;
        transfer4 = Transfer()
        for train1 in train1_set:
            train1_price_set = TrainPriceList.objects.filter(owner=train1.id)
            train1_price = 999999999
            for train1_price_temp in train1_price_set:
                if train1_price_temp.price < train1_price:
                    train1_price = train1_price_temp.price
            arrival1 = self.getCity(train1.endstation)
            date1 = train1.arrivaldate
            time1 = train1.arrivaltime
            flight2_set = Flight.objects.filter(city=arrival1, endcity=arrival, departdate=date1, departtime__gte=time1)
            for flight2 in flight2_set:
                total_price = train1_price + flight2.minprice
                if total_price < min_price:
                    min_price = total_price
                    transfer4.id1 = train1.id
                    transfer4.type1 = '火车'
                    transfer4.id2 = flight2.id
                    transfer4.type2 = '飞机'
        transfer = [transfer1, transfer2, transfer3, transfer4]

        return Response(self.serializer_class_transfer(transfer, many=True).data, status=status.HTTP_200_OK)

    def getCity(self, station):
        if station[-1] == '东':
            return station[:-1]
        if station[-1] == '西':
            return station[:-1]
        if station[-1] == '南':
            return station[:-1]
        if station[-1] == '北':
            return station[:-1]
        if station[-1] == '桥' and station[-2] == '虹':
            return station[:-2]
        return station

    @action(methods=['GET'], detail=False, url_path='getThroughTrain')
    def getThroughTrain(self, request, *args, **kwargs):
        departure = request.GET.get('departure')
        arrival = request.GET.get('arrival')
        date = request.GET.get('date')
        train_set = Train.objects.filter(station__icontains=departure, endstation__icontains=arrival, departdate=date)
        return Response(self.serializer_class(train_set, many=True).data, status=status.HTTP_200_OK)