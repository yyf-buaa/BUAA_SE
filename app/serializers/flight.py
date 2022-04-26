from rest_framework import serializers
from app.models.flight import Flight,FlightPriceList
from utilities.mixins import PrimaryKeyNestedField
class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        exclude = []

class FlightPriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightPriceList
        exclude = []

        