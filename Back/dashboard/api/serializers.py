# dashboard/api/serializers.py
from rest_framework import serializers

class DashboardSummarySerializer(serializers.Serializer):
    cash_balance       = serializers.IntegerField()
    total_invested     = serializers.FloatField()
    overall_profit_rate= serializers.FloatField()

class HoldingSerializer(serializers.Serializer):
    type         = serializers.CharField()  # "stock" 또는 "product"
    name         = serializers.CharField()
    quantity     = serializers.IntegerField()
    current_price= serializers.FloatField()
    profit_rate  = serializers.FloatField()

class TradeSerializer(serializers.Serializer):
    trade_type  = serializers.CharField()
    stock_code  = serializers.CharField()
    quantity    = serializers.IntegerField()
    price       = serializers.IntegerField()
    traded_at   = serializers.DateTimeField()
    strategy    = serializers.CharField(allow_null=True)

class StrategySummarySerializer(serializers.Serializer):
    count           = serializers.IntegerField()
    average_return  = serializers.FloatField()
    best_strategy   = serializers.CharField(allow_null=True)
