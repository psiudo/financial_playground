# simulator/serializers.py

from rest_framework import serializers
from .models import VirtualTrade
from insight.models import InterestStock

class VirtualTradeSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='stock.company_name', read_only=True)

    class Meta:
        model = VirtualTrade
        fields = ['id', 'stock_name', 'is_buy', 'quantity', 'price', 'traded_at']
