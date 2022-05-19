from rest_framework import serializers
from app.models import Position, Address, Companion, TagOnCompanion, Tag, TagOnTravel
from utilities import mixins
from .user import UserSerializer
from utilities.mixins import PrimaryKeyNestedField
from .address import AddressSerializer
from .travel import TravelSerializer, Travel
from .companion import CompanionSerializer
from .images import Image


class TagSerializer(serializers.ModelSerializer):
    user= PrimaryKeyNestedField(serializer=UserSerializer, required=False)
    class Meta:
        model = Tag
        exclude = ['forbidden_reason']


class TagOnTravelSerializer(serializers.ModelSerializer):
    tag = PrimaryKeyNestedField(serializer=TagSerializer, required=False)
    class Meta:
        model = TagOnTravel
        exclude = []


class TaggedTravelSerializer(serializers.ModelSerializer):
    taggedTravel = TagOnTravelSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        exclude = []


class TagOnCompanionSerializer(serializers.ModelSerializer):
    tag = PrimaryKeyNestedField(serializer=TagSerializer, required=False)
    class Meta:
        model = TagOnCompanion
        exclude = []


class TaggedCompanionSerializer(serializers.ModelSerializer):
    taggedCompanion = TagOnCompanionSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        exclude = []


class TagAndTravelSerializer(serializers.ModelSerializer):
    travel = TravelSerializer(many=False)

    class Meta:
        model = TagOnTravel
        exclude = ['id', 'tag']
        
        
class TagAndCompanionSerializer(serializers.ModelSerializer):
    companion = CompanionSerializer(many=False)
    class Meta:
        model = TagOnCompanion
        exclude = ['id', 'tag']
        