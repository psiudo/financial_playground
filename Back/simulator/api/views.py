# simulator/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from simulator.models import VirtualPortfolio
from .serializers import PortfolioSerializer, BuySellSerializer


class PortfolioView(generics.RetrieveAPIView):
    """
    GET /api/simulator/portfolio/
    로그인 사용자의 가상 포트폴리오와 거래 내역을 반환
    """
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        portfolio, _ = VirtualPortfolio.objects.get_or_create(user=self.request.user)
        return (
            VirtualPortfolio.objects
            .prefetch_related("trades")
            .get(pk=portfolio.pk)
        )


class TradeView(generics.GenericAPIView):
    """
    POST /api/simulator/trade/
    매수 또는 매도 요청을 처리한다
    """
    serializer_class = BuySellSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        portfolio, _ = VirtualPortfolio.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(
            data=request.data,
            context={"portfolio": portfolio},
        )
        serializer.is_valid(raise_exception=True)
        trade = serializer.save()
        portfolio.refresh_from_db()
        return Response(
            {
                "portfolio": PortfolioSerializer(portfolio).data,
                "trade_id": trade.id,
            },
            status=status.HTTP_201_CREATED,
        )
