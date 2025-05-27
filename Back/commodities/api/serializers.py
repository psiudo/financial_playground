# back/commodities/api/serializers.py
from rest_framework import serializers
from commodities.models import Commodity, PriceHistory


class CommodityListSerializer(serializers.ModelSerializer):
    latest_price = serializers.SerializerMethodField()

    class Meta:
        model  = Commodity
        fields = ["symbol", "name", "latest_price"]

    def get_latest_price(self, obj):
        latest = obj.prices.order_by("-date").first()
        return latest.price if latest else None


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = PriceHistory
        fields = ["date", "price"]
