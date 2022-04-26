from rest_framework import viewsets
from app.models.position import EpidemicControlInfo
from app.response import *
from rest_framework.decorators import action
from app.serializers.epidemic_info import EpidemicInfoSerializer

class EpidemicInfoApis(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin):
    queryset = EpidemicControlInfo.objects.all()
    serializer_class = EpidemicInfoSerializer
    #传入position返回此地的防疫信息
    @action(methods=['GET'], detail=False, url_path='getInfo')
    def getInfo(self,request,*args, **kwargs):
        position = request.GET.get('position')
        info = EpidemicControlInfo.objects.filter(position=position)
        if len(info)==0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        s = self.serializer_class(info,many=True)
        return Response(s.data,status=status.HTTP_200_OK)



