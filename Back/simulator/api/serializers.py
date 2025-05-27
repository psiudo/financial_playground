# Back/simulator/api/serializers.py
from rest_framework import serializers
from simulator.models import VirtualPortfolio, VirtualTrade


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualTrade
        fields = [
            "id",
            "trade_type",
            "stock_code",
            "stock_name",
            "price",
            "quantity",
            "traded_at",
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    trades = TradeSerializer(many=True, read_only=True)

    class Meta:
        model = VirtualPortfolio
        fields = ["id", "cash_balance", "created_at", "trades"]


class BuySellSerializer(serializers.Serializer):
    trade_type = serializers.ChoiceField(choices=[("buy", "매수"), ("sell", "매도")])
    stock_code = serializers.CharField(max_length=12)
    stock_name = serializers.CharField(max_length=100)
    price = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        if data["trade_type"] == "buy":
            need_cash = data["price"] * data["quantity"]
            portfolio = self.context["portfolio"]
            if portfolio.cash_balance < need_cash:
                raise serializers.ValidationError("잔액이 부족합니다")
        return data

    def create(self, validated_data):
        portfolio = self.context["portfolio"]
        trade_type = validated_data["trade_type"]
        price = validated_data["price"]
        qty = validated_data["quantity"]

        from django.db import transaction
        from django.db.models import F

        with transaction.atomic():
            if trade_type == "buy":
                portfolio.cash_balance = F("cash_balance") - price * qty
            else:
                portfolio.cash_balance = F("cash_balance") + price * qty
            portfolio.save(update_fields=["cash_balance"])
            portfolio.refresh_from_db(fields=["cash_balance"])

            trade = VirtualTrade.objects.create(
                portfolio=portfolio,
                **validated_data,
            )
        return trade
