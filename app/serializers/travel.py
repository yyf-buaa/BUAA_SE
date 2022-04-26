from rest_framework import serializers
from app.models import Travel, Position, Address
from .user import UserSerializer, AppUser
from .address import AddressSerializer
from .images import Image
from utilities import mixins

class TravelSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    owner = mixins.PrimaryKeyNestedField(serializer=UserSerializer)#serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all())
    cover = serializers.PrimaryKeyRelatedField(read_only=True)
    images = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    position = AddressSerializer(required=False, allow_null=True)
    likes = serializers.SerializerMethodField('count_likes')
    comments = serializers.SerializerMethodField('count_comments')

    def count_likes(self, obj):
        return obj.likes.count()

    def count_comments(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        position = validated_data.get('position', None)
        if position is not None:
            validated_data['position'] = Address.objects.create(**position)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        position = validated_data.get('position', None)
        if position is not None:
            if instance.position:
                validated_data['position'], *_ = Address.objects.update_or_create(defaults=position, id=instance.position_id)
            else:
                validated_data['position'] = Address.objects.create(**position)
        return super().update(instance, validated_data)

    class Meta:
        model = Travel
        exclude = ['forbidden_reason']

class TravelAddressSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    position = AddressSerializer(read_only=True)

    class Meta:
        model = Travel
        fields = ['id', 'position', 'time']
