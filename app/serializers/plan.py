from rest_framework import serializers
from app.models.flight import Flight,FlightPriceList
from app.models.plan import Plan,Plan_Ser,Plan_Comp
from utilities.mixins import PrimaryKeyNestedField
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        exclude = []
class PlanSerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan_Ser
        exclude = ['id']

class PlanCompSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan_Comp
        exclude = []