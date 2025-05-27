# back/marketplace/api/serializers.py
from rest_framework import serializers
from marketplace.models import MarketListing, Purchase
from strategies.models import Strategy

class MarketListingSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source="seller.username")
    strategy_name = serializers.ReadOnlyField(source="strategy.name")

    class Meta:
        model = MarketListing
        fields = [
            "id",
            "strategy",
            "strategy_name",
            "seller",
            "price_point",
            "sales",
            "created_at",
        ]

class MarketListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketListing
        fields = ["strategy", "price_point"]

    def validate_strategy(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("본인 소유 전략만 마켓에 등록할 수 있습니다")
        if MarketListing.objects.filter(strategy=value).exists():
            raise serializers.ValidationError("이미 등록된 전략입니다")
        return value

class PurchaseSerializer(serializers.ModelSerializer):
    buyer = serializers.ReadOnlyField(source="buyer.username")
    listing_detail = MarketListingSerializer(source="listing", read_only=True)

    class Meta:
        model = Purchase
        fields = ["id", "buyer", "listing", "listing_detail", "purchased_at"]
