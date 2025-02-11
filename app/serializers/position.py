from rest_framework import serializers
from app.models.position import Position


class PositionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    cover = serializers.PrimaryKeyRelatedField(read_only=True)
    images = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Position
        exclude = ['visibility', 'heat']


class PositionHeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        exclude = ['visibility']