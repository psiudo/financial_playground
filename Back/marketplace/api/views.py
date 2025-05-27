# back/marketplace/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from marketplace.models import MarketListing, Purchase
from .serializers import (
    MarketListingSerializer,
    MarketListingCreateSerializer,
    PurchaseSerializer,
)
from accounts.models import PointTransaction
from notifications.models import Notification

class MarketListingListCreateAPIView(generics.ListCreateAPIView):
    queryset = MarketListing.objects.select_related("strategy", "seller").all()
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method == "POST":
            return MarketListingCreateSerializer
        return MarketListingSerializer

class MarketListingRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = MarketListing.objects.all()
    serializer_class = MarketListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        listing = self.get_object()
        user = self.request.user
        if listing.seller != user:
            raise PermissionError("본인 판매 목록만 수정할 수 있습니다")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.seller != self.request.user:
            raise PermissionError("본인 판매 목록만 삭제할 수 있습니다")
        instance.delete()

class PurchaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        buyer = request.user
        listing = get_object_or_404(MarketListing, pk=pk)
        if listing.seller == buyer:
            return Response({"error": "본인 전략은 구매할 수 없습니다"},
                            status=status.HTTP_400_BAD_REQUEST)
        if Purchase.objects.filter(buyer=buyer, listing=listing).exists():
            return Response({"error": "이미 구매한 전략입니다"},
                            status=status.HTTP_400_BAD_REQUEST)
        price = listing.price_point
        if buyer.point_balance < price:
            return Response({"error": "포인트가 부족합니다"},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # 포인트 차감·적립
            buyer.point_balance -= price
            buyer.save(update_fields=["point_balance"])
            PointTransaction.objects.create(
                user=buyer,
                delta_point=-price,
                kind=PointTransaction.DECREASE,
                reason="strategy_purchase"
            )
            seller = listing.seller
            seller.point_balance += price
            seller.save(update_fields=["point_balance"])
            PointTransaction.objects.create(
                user=seller,
                delta_point=price,
                kind=PointTransaction.INCREASE,
                reason="strategy_sale"
            )
            # 판매 수 증가
            listing.sales = listing.sales + 1
            listing.save(update_fields=["sales"])
            # 구매 기록
            purchase = Purchase.objects.create(
                buyer=buyer,
                listing=listing
            )
            # 알림 생성
            Notification.objects.create(
                user=seller,
                verb="전략이 판매되었습니다",
                target=purchase,
                message=f"{buyer.username}님이 {listing.strategy.name} 전략을 구매하였습니다",
                link=f"/strategies/{listing.strategy.id}/"
            )

        serializer = PurchaseSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PurchaseListAPIView(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Purchase.objects.filter(buyer=self.request.user)
