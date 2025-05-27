# Back/marketplace/api/serializers.py
from rest_framework import serializers
from marketplace.models import MarketListing, Purchase
from strategies.api.serializers import StrategySerializer # 수정된 StrategySerializer import
from strategies.models import Strategy 

class MarketListingSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source="seller.username")
    strategy = StrategySerializer(read_only=True) 

    class Meta:
        model = MarketListing
        fields = [
            "id",
            "strategy", 
            "seller",
            "price_point",
            "sales",
            "created_at",
        ]

class MarketListingCreateSerializer(serializers.ModelSerializer):
    strategy = serializers.PrimaryKeyRelatedField(queryset=Strategy.objects.all())

    class Meta:
        model = MarketListing
        fields = ["strategy", "price_point"] 

    def validate_strategy(self, value_strategy_instance):
        request_user = self.context["request"].user
        if value_strategy_instance.user != request_user:
            raise serializers.ValidationError("본인 소유의 전략만 마켓플레이스에 등록할 수 있습니다.")
        if MarketListing.objects.filter(strategy=value_strategy_instance, seller=request_user).exists():
            raise serializers.ValidationError("이미 마켓플레이스에 등록한 전략입니다.")
        return value_strategy_instance

class PurchaseSerializer(serializers.ModelSerializer):
    buyer = serializers.ReadOnlyField(source="buyer.username")
    listing = MarketListingSerializer(read_only=True) 

    class Meta:
        model = Purchase
        # 'cloned_strategy_id'는 Purchase 모델의 필드가 아니므로 여기서 제거합니다.
        fields = ["id", "buyer", "listing", "purchased_at"]
        # extra_kwargs에서 'cloned_strategy_id' 관련 부분도 제거합니다.