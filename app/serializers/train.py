from rest_framework import serializers
from app.models.train import Train, TrainPriceList
from utilities.mixins import PrimaryKeyNestedField

class SingleTrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        exclude = []


class TrainPriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainPriceList
        exclude = []


class TrainSerializer(serializers.ModelSerializer):
    prices = TrainPriceListSerializer(many=True, read_only=True)

    class Meta:
        model = Train
        exclude = []


class PriceTrainListSerializer(serializers.ModelSerializer):
    owner = SingleTrainSerializer(read_only=True)

    class Meta:
        model = TrainPriceList
        exclude = []
