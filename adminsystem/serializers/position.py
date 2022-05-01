from rest_framework import serializers
from app.models.position import Position, EpidemicControlInfo

class EpidemicControlInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpidemicControlInfo
        exclude = []


class PositionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    cover = serializers.PrimaryKeyRelatedField(read_only=True)
    images = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    epidemic = EpidemicControlInfoSerializer(many=True)

    class Meta:
        model = Position
        exclude = []
