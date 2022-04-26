from rest_framework import serializers
from app.models.blackPos import BlackPos
class BlackPosSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackPos
        exclude = []
