# back/strategies/api/serializers.py
from rest_framework import serializers
from strategies.models import Strategy, StrategyRun, StrategyTrade

class StrategySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Strategy
        fields = [
            'id', 'user', 'name', 'description',
            'rule_json', 'is_public', 'is_paid',
            'price_point', 'created_at',
        ]

class StrategyRunSerializer(serializers.ModelSerializer):
    strategy = serializers.ReadOnlyField(source='strategy.id')

    class Meta:
        model = StrategyRun
        fields = ['id', 'strategy', 'started_at', 'ended_at', 'total_return']

class StrategyTradeSerializer(serializers.ModelSerializer):
    run = serializers.ReadOnlyField(source='run.id')

    class Meta:
        model = StrategyTrade
        fields = ['id', 'run', 'stock_code', 'trade_type', 'price', 'quantity', 'traded_at']
