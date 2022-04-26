from rest_framework import serializers
from app.models.images import Image
import os
from app.models.position import Position
from app.models.position import EpidemicControlInfo
from app.serializers.position import PositionSerializer
from utilities.mixins import PrimaryKeyNestedField
class EpidemicInfoSerializer(serializers.ModelSerializer):
    description = serializers.CharField(read_only=True)
    position = PrimaryKeyNestedField(serializer=PositionSerializer)

    class Meta:
        model = EpidemicControlInfo
        exclude = []
