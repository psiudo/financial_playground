# back/commodities/api/views.py
from rest_framework import generics
from django.shortcuts import get_object_or_404
from commodities.models import Commodity
from .serializers import CommodityListSerializer, PriceHistorySerializer


class CommodityListAPIView(generics.ListAPIView):
    queryset = Commodity.objects.all().prefetch_related("prices")
    serializer_class = CommodityListSerializer


class CommodityHistoryAPIView(generics.ListAPIView):
    serializer_class = PriceHistorySerializer

    def get_queryset(self):
        symbol = self.kwargs["symbol"]
        # symbol = self.kwargs["symbol"].upper()  # 대소문자 구분 없이 처리하려면 주석 해제하고 위 줄 주석석
        commodity = get_object_or_404(Commodity, symbol=symbol)
        qs = commodity.prices.all()
        date_from = self.request.query_params.get("from")
        date_to   = self.request.query_params.get("to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs.order_by("date")
