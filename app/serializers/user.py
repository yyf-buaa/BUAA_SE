from rest_framework import serializers
from app.models import AppUser, Address, Position,Companion,Plan,Plan_Ser
from .address import AddressSerializer
from utilities import encrypt, location
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    position = AddressSerializer(required=False, allow_null=True)
    cities = serializers.SerializerMethodField('count_cities')
    travels = serializers.SerializerMethodField('count_travels')
    subscription = serializers.SerializerMethodField('count_subscription')
    subscribers = serializers.SerializerMethodField('count_subscribers')

    def count_subscription(self, obj: AppUser):
        return obj.subscription.count()

    def count_subscribers(self, obj: AppUser):
        return obj.subscribers.count()

    def count_cities(self, obj: AppUser):
        d1 = timezone.now()
        today = d1.strftime("%Y-%m-%d")
        num1 = Address.objects.filter(travel_record__owner=obj).values_list('position__id', flat=True).distinct().count()
        plan_set = Plan.objects.filter(owner = obj,date__lte=today)
        pos_set = set()
        for plan in plan_set:
            # 根据content split
            content = plan.content
            transfer = content.split('-')
            if len(transfer) == 1:
                # 直达
                result = Plan_Ser()
                content1 = transfer[0]
                result.type = '直达'
                result.id1 = content1.split(':')[0]
                result.type1 = content1.split(':')[1]
                result.from1 = content1.split(':')[2].split('+')[0]
                result.to1 = content1.split(':')[2].split('+')[1]
                result.id2 = None
                result.type2 = None
                result.from2 = None
                result.to2 = None
                pos_set.add(result.from1)
                pos_set.add(result.to1)
            else:
                # 换乘
                result = Plan_Ser()
                content1 = transfer[0]
                content2 = content1 = transfer[1]
                result.type = '换乘'
                result.id1 = content1.split(':')[0]
                result.type1 = content1.split(':')[1]
                result.from1 = content1.split(':')[2].split('+')[0]
                result.to1 = content1.split(':')[2].split('+')[1]
                result.id2 = content2.split(':')[0]
                result.type2 = content2.split(':')[1]
                result.from2 = content2.split(':')[2].split('+')[0]
                result.to2 = content2.split(':')[2].split('+')[1]
                pos_set.add(result.from1)
                pos_set.add(result.to1)
                pos_set.add(result.to2)
        num2 = len(pos_set)
        return num1+num2


    def count_travels(self, obj: AppUser):
        num1 = obj.travel_records.count()
        d1 = timezone.now()
        today = d1.strftime("%Y-%m-%d")
        plan_set = Plan.objects.filter(owner=obj, date__lte=today)
        num2 = len(plan_set)
        return num1+num2

    def validate_position(self, value):
        return value

    def create(self, validated_data):
        position = validated_data.get('position', None)
        if position is not None:
            validated_data['position'] = Address.objects.create(**position)
        return super().create(validated_data)

    def update(self, instance: AppUser, validated_data):
        position = validated_data.get('position', None)
        if position is not None:
            if instance.position:
                validated_data['position'], *_ = Address.objects.update_or_create(defaults=position, id=instance.position_id)
            else:
                validated_data['position'] = Address.objects.create(**position)
        return super().update(instance, validated_data)

    class Meta:
        model = AppUser
        exclude = ['time', 'password', 'collection', 'received_messages', 'blackList', 'unread_messages', 'openid', 'cluster', 'last_admin_message_time']
        # 别删blackList,不然注册不了用户
