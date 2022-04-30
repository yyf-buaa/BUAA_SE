from rest_framework import serializers
from app.models.Transfer import Transfer
class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        exclude = []
