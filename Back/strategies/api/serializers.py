# Back/strategies/api/serializers.py
from rest_framework import serializers
from strategies.models import Strategy, StrategyRun, StrategyTrade
# from marketplace.models import Purchase # 직접 임포트 최소화 (필요시 함수 내에서)

class StrategySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    is_purchased = serializers.SerializerMethodField()
    is_listed_on_marketplace = serializers.SerializerMethodField()

    class Meta:
        model = Strategy
        fields = [
            'id', 'user', 'name', 'description',
            'rule_json', 'is_public', 'is_paid',
            'price_point', 'created_at', 
            'is_purchased', 'is_listed_on_marketplace',
        ]
        read_only_fields = ['user', 'created_at']

    def get_is_purchased(self, obj_strategy):
        request = self.context.get('request', None)
        listing_id = self.context.get('listing_id', None) 

        if not request or not request.user.is_authenticated or not listing_id:
            return False
        
        from marketplace.models import Purchase, MarketListing # 함수 내 지역 임포트
        try:
            listing = MarketListing.objects.get(pk=listing_id)
            # 현재 Serializer가 다루는 Strategy 객체(obj_strategy)가
            # context로 전달된 listing_id에 해당하는 MarketListing의 strategy와 동일한지 확인
            if listing.strategy_id != obj_strategy.id:
                return False 
            return Purchase.objects.filter(listing_id=listing_id, buyer=request.user).exists()
        except MarketListing.DoesNotExist:
            return False

    def get_is_listed_on_marketplace(self, obj_strategy):
        # Strategy 모델에 MarketListing과의 역참조 관계 이름이 'marketlisting' (OneToOneField)이라고 가정
        return hasattr(obj_strategy, 'marketlisting') and obj_strategy.marketlisting is not None

    def to_representation(self, instance_strategy):
        representation = super().to_representation(instance_strategy)
        request = self.context.get('request')
        
        can_view_rule_json = False

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if instance_strategy.user == request.user: # 1. 소유자
                can_view_rule_json = True
            elif representation.get('is_purchased'): # 2. 구매자
                 can_view_rule_json = True
        
        # 3. 마켓플레이스 공개 정책 (구매 전)
        if not can_view_rule_json and \
           instance_strategy.is_public and \
           representation.get('is_listed_on_marketplace'):
            # 유료 전략(is_paid=True 또는 price_point > 0)은 구매해야만 rule_json 공개
            # 무료 공개 전략은 rule_json 보여줌
            if instance_strategy.is_paid or instance_strategy.price_point > 0:
                # 이 부분에서 유료 전략의 rule_json을 구매 전에 얼마나 보여줄지 결정합니다.
                # 아예 안 보여주려면 'pass' 또는 can_view_rule_json = False를 명시합니다.
                # 여기서는 일단 구매해야만 볼 수 있도록 False로 유지합니다. (사용자님 의견에 따라 수정 가능)
                pass # can_view_rule_json은 False 유지
            else: # 무료로 공개된 전략은 rule_json 보여줌
                can_view_rule_json = True
        
        if not can_view_rule_json:
            representation.pop('rule_json', None)
            
        return representation

class StrategyRunSerializer(serializers.ModelSerializer):
    strategy_id = serializers.PrimaryKeyRelatedField(read_only=True, source='strategy.id')
    strategy_name = serializers.CharField(read_only=True, source='strategy.name')

    class Meta:
        model = StrategyRun
        fields = ['id', 'strategy_id', 'strategy_name', 'started_at', 'ended_at', 'total_return']

class StrategyTradeSerializer(serializers.ModelSerializer):
    run_id = serializers.PrimaryKeyRelatedField(read_only=True, source='run.id')

    class Meta:
        model = StrategyTrade
        fields = ['id', 'run_id', 'stock_code', 'trade_type', 'price', 'quantity', 'traded_at']