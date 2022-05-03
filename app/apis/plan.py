from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAcceptable, PermissionDenied
from rest_framework.decorators import action
from django.http import QueryDict

from django.conf import settings
from app.models import AdminMessage, AppUser,Plan,Plan_Ser
from app.serializers import AdminMessageSerializer,PlanSerSerializer
from app.utilities import permission
from app.response import *
from utilities import conversion, filters, permission as _permission, date

class PlanApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin):
    queryset = Plan.objects.all()
    serializer_class = PlanSerSerializer
    #加入我的出行计划
    @action(methods=['POST'], detail=False, url_path='addMyPlan')
    def addMyPlan(self,request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        type = request.data.get('type')
        if type=='直达':
            id1 = request.data.get('id1')
            type1 = request.data.get('type1')
            from1 = request.data.get('from1')
            to1 = request.data.get('to1')
            plan = Plan()
            plan.owner = AppUser.objects.filter(id=request_user).first()
            plan.content = id1+':'+type1+':'+from1+'+'+to1
            plan.save()
        else:
            id1 = request.data.get('id1')
            type1 = request.data.get('type1')
            from1 = request.data.get('from1')
            to1 = request.data.get('to1')
            id2 = request.data.get('id2')
            type2 = request.data.get('type2')
            from2 = request.data.get('from2')
            to2 = request.data.get('to2')
            plan = Plan()
            plan.owner = AppUser.objects.filter(id=request_user).first()
            plan.content = id1 + ':' + type1+':'+from1+'+'+to1+'-'+id2 + ':' + type2+':'+from2+'+'+to2
            plan.save()
        return Response(True,status=status.HTTP_200_OK)

    #查询自己的出行计划
    @action(methods=['GET'], detail=False, url_path='getMyPlan')
    def getMyPlan(self,request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        plan_set = Plan.objects.filter(owner = request_user)
        result_list = []
        for plan in plan_set:
            #根据content split
            content = plan.content
            transfer = content.split('-')
            if len(transfer) == 1:
                #直达
                result = Plan_Ser()
                content1 = transfer[0]
                result.type = '直达'
                result.id1 = content1.split(':')[0]
                result.type1 = content1.split(':')[1]
                result.from1 = content1.split(':')[2].split('+')[0]
                result.to1 = content1.split(':')[2].split('+')[1]
                result.id2 = None
                result.type2 = None
                result.from2 = None
                result.to2 = None
            else:
                #换乘
                result = Plan_Ser()
                content1 = transfer[0]
                content2 = content1 = transfer[1]
                result.type = '换乘'
                result.id1 = content1.split(':')[0]
                result.type1 = content1.split(':')[1]
                result.from1 = content1.split(':')[2].split('+')[0]
                result.to1 = content1.split(':')[2].split('+')[1]
                result.id2 = content2.split(':')[0]
                result.type2 = content2.split(':')[1]
                result.from2 = content2.split(':')[2].split('+')[0]
                result.to2 = content2.split(':')[2].split('+')[1]
            result_list.append(result)
        return Response(PlanSerSerializer(result_list,many=True).data,status = status.HTTP_200_OK)

    #查询一个交通计划是否已经添加
    @action(methods=['POST'], detail=False, url_path='searchMyPlan')
    def searchMyPlan(self,request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        type = request.data.get('type')
        if type == '直达':
            id1 = request.data.get('id1')
            type1 = request.data.get('type1')
            from1 = request.data.get('from1')
            to1 = request.data.get('to1')
            owner = AppUser.objects.filter(id=request_user).first()
            content = id1 + ':' + type1 + ':' + from1 + '+' + to1
            plan_set = Plan.objects.filter(owner = owner,content=content)
            if len(plan_set)>0:
                return Response(True, status=status.HTTP_200_OK)
            else:
                return Response(False, status=status.HTTP_200_OK)
        else:
            id1 = request.data.get('id1')
            type1 = request.data.get('type1')
            from1 = request.data.get('from1')
            to1 = request.data.get('to1')
            id2 = request.data.get('id2')
            type2 = request.data.get('type2')
            from2 = request.data.get('from2')
            to2 = request.data.get('to2')
            owner = AppUser.objects.filter(id=request_user).first()
            content = id1 + ':' + type1 + ':' + from1 + '+' + to1 + '-' + id2 + ':' + type2 + ':' + from2 + '+' + to2
            plan_set = Plan.objects.filter(owner=owner, content=content)
            if len(plan_set) > 0:
                return Response(True, status=status.HTTP_200_OK)
            else:
                return Response(False, status=status.HTTP_200_OK)

    #删除一个出行计划
    @action(methods=['POST'], detail=False, url_path='deleteMyPlan')
    def deleteMyPlan(self,request, *args, **kwargs):
        request_user = _permission.user_check(request)
        if request_user <= 0:
            return error_response(Error.NOT_LOGIN, 'Please login.', status=status.HTTP_403_FORBIDDEN)
        type = request.data.get('type')
        if type == '直达':
            id1 = request.data.get('id1')
            type1 = request.data.get('type1')
            from1 = request.data.get('from1')
            to1 = request.data.get('to1')
            owner = AppUser.objects.filter(id=request_user).first()
            content = id1 + ':' + type1 + ':' + from1 + '+' + to1
            Plan.objects.filter(owner = owner,content=content).delete()
        else:
            id1 = request.data.get('id1')
            type1 = request.data.get('type1')
            from1 = request.data.get('from1')
            to1 = request.data.get('to1')
            id2 = request.data.get('id2')
            type2 = request.data.get('type2')
            from2 = request.data.get('from2')
            to2 = request.data.get('to2')
            owner = AppUser.objects.filter(id=request_user).first()
            content = id1 + ':' + type1 + ':' + from1 + '+' + to1 + '-' + id2 + ':' + type2 + ':' + from2 + '+' + to2
            Plan.objects.filter(owner=owner, content=content).delete()
        return Response(True,status=status.HTTP_200_OK)