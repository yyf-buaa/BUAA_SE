from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied
from rest_framework.decorators import action

from app.models import Flight,FlightPriceList
from app.serializers import FlightSerializer,FlightPriceListSerializer
from app.utilities import permission
from app.response import *
from utilities import conversion, filters, permission as _permission

class FlightApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    queryset_price = FlightPriceList.objects.all()
    serializer_class_price = FlightPriceListSerializer
    
    # 传入flight_id返回航班的详细信息
    @action(methods=['GET'], detail=False, url_path='getFlightInfo')
    def getFlightInfo(self,request,*args, **kwargs):
        flight_id = request.GET.get('flightid')
        flight = Flight.objects.filter(id = flight_id)
        serializer_flight = self.serializer_class(flight,many=True)
        return Response(serializer_flight.data,status=status.HTTP_200_OK)
        
    # 传入航班表的id返回这趟航班对应的价格表
    @action(methods=['GET'], detail=False, url_path='getPriceList')
    def getPriceList(self,request,*args, **kwargs):
        id = request.GET.get('id')
        priceList = FlightPriceList.objects.filter(owner_id = id)
        serializer_price = self.serializer_class_price(priceList,many=True)
        return Response(serializer_price.data,status=status.HTTP_200_OK)
        
    # 传入'航班号,出发地,目的地'获取航班详细信息
    @action(methods=['GET'], detail=False, url_path='getFlightNo')
    def getFlightNo(self, request, *args, **kwargs):
        flight_no = request.GET.get('flightno')
        departure = request.GET.get('departure')
        arrival = request.GET.get('arrival')
        # 查询航班号的信息 至 列表flight_list
        flight = Flight.objects.filter(flightno=flight_no)
        flight_list = self.serializer_class(flight, many=True)
        # 返回符合出发地-目的地的航班信息
        for i in flight_list.data:
            if i['city'] == departure and i['endcity'] == arrival:
                i['departtime'] = i['departtime'][:-3]
                i['arrivaltime'] = i['arrivaltime'][:-3]
                i['departport'] = i['departport'] + ' ' + i['departterminal']
                i['arrivalport'] = i['arrivalport'] + ' ' + i['arrivalterminal']
                return Response(i)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
    # 地点廉航推荐
    @action(methods=['GET'], detail=False, url_path='getCheapFlight')
    def getCheapFlight(self, request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        departure = Position.objects.filter(adcode=AppUser.objects.filter(id=request_user).first().position_id).first().name
        arrival = request.GET.get('position')
        flight = Flight.objects.filter(city__icontains=departure, endcity=arrival).order_by('minprice')
        serializer_flight = self.serializer_class(flight, many=True)
        return Response(serializer_flight, status=status.HTTP_400_BAD_REQUEST)