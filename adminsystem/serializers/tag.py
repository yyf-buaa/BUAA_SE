from rest_framework import serializers
from app.models import Position, Address, Companion, TagOnCompanion, Tag, TagOnTravel
from utilities import mixins
from .user import UserSerializer
from utilities.mixins import PrimaryKeyNestedField


class TagSerializer(serializers.ModelSerializer):
    user= PrimaryKeyNestedField(serializer=UserSerializer, required=False)
    class Meta:
        model = Tag
        exclude = []
    

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
