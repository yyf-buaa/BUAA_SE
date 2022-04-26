from rest_framework import serializers
from app.models.train import Train, TrainPriceList
from utilities.mixins import PrimaryKeyNestedField


class TrainPriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainPriceList
        exclude = []


class TrainSerializer(serializers.ModelSerializer):
    prices = TrainPriceListSerializer(many=True, read_only=True)

    class Meta:
        model = Train
        exclude = []


