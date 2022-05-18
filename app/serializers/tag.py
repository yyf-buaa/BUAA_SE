from rest_framework import serializers
from app.models import Position, Address, Companion, TagOnCompanion, Tag, TagOnTravel
from .user import UserSerializer, AppUser
from .address import AddressSerializer
from .travel import TravelSerializer, Travel
from .companion import CompanionSerializer
from .images import Image
from utilities import mixins


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        exclude = ['forbidden_reason']


class TagOnTravelSerializer(serializers.ModelSerializer):
    travel = TravelSerializer(many=False)

    class Meta:
        model = TagOnTravel
        exclude = ['id', 'tag']


class TaggedTravelSerializer(serializers.ModelSerializer):
    taggedTravel = TagOnTravelSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        exclude = []


class TagOnCompanionSerializer(serializers.ModelSerializer):
    companion = CompanionSerializer(many=False)
    class Meta:
        model = TagOnCompanion
        exclude = ['id', 'tag']


class TaggedCompanionSerializer(serializers.ModelSerializer):
    taggedCompanion = TagOnCompanionSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        exclude = []
