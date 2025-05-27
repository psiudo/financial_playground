# Back/marketplace/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import F # <<<!!! 이 부분을 추가해주세요 !!!>>>

from marketplace.models import MarketListing, Purchase
from .serializers import (
    MarketListingSerializer,
    MarketListingCreateSerializer,
    PurchaseSerializer,
)
from accounts.models import PointTransaction, CustomUser 
from notifications.models import Notification
from strategies.models import Strategy 

class MarketListingListCreateAPIView(generics.ListCreateAPIView):
    queryset = MarketListing.objects.select_related("strategy", "strategy__user", "seller").all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MarketListingSerializer
        return MarketListingCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        if hasattr(self, 'object') and self.object:
             context['listing_id'] = self.object.id
        return context

    def perform_create(self, serializer):
        strategy_pk = self.request.data.get('strategy')
        price_point_str = self.request.data.get('price_point')

        if not strategy_pk:
            raise ValidationError({"strategy": "전략 ID를 입력해야 합니다."})
        if price_point_str is None: 
            raise ValidationError({"price_point": "가격을 입력해야 합니다."})

        try:
            price_point = int(price_point_str)
            if price_point < 0: 
                raise ValueError
        except ValueError:
            raise ValidationError({"price_point": "유효한 가격(0 이상의 정수)을 입력해야 합니다."})

        strategy_instance = get_object_or_404(Strategy, pk=strategy_pk, user=self.request.user)

        if MarketListing.objects.filter(strategy=strategy_instance, seller=self.request.user).exists():
            raise ValidationError({"strategy": "이미 마켓플레이스에 등록한 전략입니다."})
        
        serializer.save(seller=self.request.user, strategy=strategy_instance, price_point=price_point)


class MarketListingRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = MarketListing.objects.select_related("strategy", "strategy__user", "seller").all()
    serializer_class = MarketListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        if self.kwargs.get(self.lookup_field): 
            context['listing_id'] = self.kwargs[self.lookup_field]
        return context
    
    def perform_update(self, serializer):
        listing = self.get_object()
        if listing.seller != self.request.user:
             return Response({"detail": "본인 판매 목록만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.seller != self.request.user:
            return Response({"detail": "본인 판매 목록만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class PurchaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk): # pk는 MarketListing의 pk
        buyer = request.user
        listing = get_object_or_404(MarketListing.objects.select_related('strategy', 'seller'), pk=pk)

        if listing.seller == buyer:
            return Response({"detail": "본인 전략은 구매할 수 없습니다."},
                            status=status.HTTP_400_BAD_REQUEST)
        if Purchase.objects.filter(buyer=buyer, listing=listing).exists():
            return Response({"detail": "이미 구매한 전략입니다."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        price = listing.price_point
        
        if buyer.point_balance < price: 
            return Response({"detail": "포인트가 부족합니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        original_strategy = listing.strategy
        
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        base_cloned_strategy_name = f"{original_strategy.name} (구매 - {buyer.username} - {timestamp})"
        
        cloned_strategy_name = base_cloned_strategy_name
        counter = 0
        while Strategy.objects.filter(user=buyer, name=cloned_strategy_name).exists():
            counter += 1
            cloned_strategy_name = f"{base_cloned_strategy_name}_{counter}"

        with transaction.atomic():
            buyer.point_balance -= price
            buyer.save(update_fields=["point_balance"])
            PointTransaction.objects.create(
                user=buyer, delta_point=-price, kind=PointTransaction.DECREASE,
                reason=f"전략 구매: {original_strategy.name}"
            )
            
            seller = listing.seller
            seller.point_balance += price
            seller.save(update_fields=["point_balance"])
            PointTransaction.objects.create(
                user=seller, delta_point=price, kind=PointTransaction.INCREASE,
                reason=f"전략 판매: {original_strategy.name} (구매자: {buyer.username})"
            )
            
            listing.sales = F('sales') + 1 # F 객체 사용
            listing.save(update_fields=["sales"])
            listing.refresh_from_db(fields=['sales']) 
            
            purchase = Purchase.objects.create(buyer=buyer, listing=listing)
            
            cloned_strategy = Strategy.objects.create(
                user=buyer, 
                name=cloned_strategy_name,
                description=f"[원본 전략: {original_strategy.name} (판매자: {listing.seller.username})] {original_strategy.description}",
                rule_json=original_strategy.rule_json,
                is_public=False, 
                is_paid=False,   
                price_point=0,
            )
            
            Notification.objects.create(
                user=seller, noti_type=Notification.SYSTEM, verb="전략 판매됨",
                target=f"listing:{listing.id}", 
                message=f"회원님의 전략 '{original_strategy.name}'이(가) {buyer.username}님에게 판매되었습니다.",
                link=f"/marketplace/{listing.id}/" 
            )
            Notification.objects.create(
                user=buyer, noti_type=Notification.SYSTEM, verb="전략 구매 완료",
                target=f"strategy:{cloned_strategy.id}",
                message=f"'{original_strategy.name}' 전략을 구매하여 '{cloned_strategy.name}'(으)로 나의 전략 목록에 추가했습니다.",
                link=f"/strategies/{cloned_strategy.id}/" 
            )

        serializer_context = {'request': request, 'listing_id': listing.id}
        purchase_serializer = PurchaseSerializer(purchase, context=serializer_context)
        
        response_data = purchase_serializer.data
        response_data['cloned_strategy_id'] = cloned_strategy.id
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class PurchaseListAPIView(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return Purchase.objects.filter(buyer=self.request.user).select_related(
            'listing__strategy', 
            'listing__strategy__user', 
            'listing__seller'          
        ).order_by('-purchased_at')