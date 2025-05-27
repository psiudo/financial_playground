# dashboard/api/views.py
from rest_framework.views     import APIView
from rest_framework.response  import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models        import Sum, F, Avg, Max
from simulator.models        import VirtualPortfolio, VirtualTrade
from financial_products.models import JoinedProduct
from strategies.models       import Strategy, StrategyRun
from simulator.services.price_service import fetch_current_price
from .serializers            import (
    DashboardSummarySerializer,
    HoldingSerializer,
    TradeSerializer,
    StrategySummarySerializer,
)
import random

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1) 포트폴리오
        portfolio, _ = VirtualPortfolio.objects.get_or_create(user=user)
        cash = portfolio.cash_balance

        # 2) 주식 보유 내역 계산
        buys = VirtualTrade.objects.filter(
            portfolio=portfolio, trade_type=VirtualTrade.BUY
        )
        # 종목별 보유 수량 집계
        stock_summary = {}
        for t in buys:
            stock_summary.setdefault(t.stock_code, {
                "stock_name": t.stock_name,
                "quantity": 0,
                "invested": 0,
            })
            stock_summary[t.stock_code]["quantity"] += t.quantity
            stock_summary[t.stock_code]["invested"] += t.quantity * t.price

        holdings = []
        total_invested = 0
        total_profit   = 0
        for code, info in stock_summary.items():
            qty      = info["quantity"]
            invested = info["invested"]
            current  = fetch_current_price(info["stock_name"])
            profit   = (current * qty) - invested
            profit_rate = (profit / invested * 100) if invested else 0
            holdings.append({
                "type": "stock",
                "name": info["stock_name"],
                "quantity": qty,
                "current_price": float(current),
                "profit_rate": round(profit_rate, 2),
            })
            total_invested += invested
            total_profit   += profit

        # 3) 금융상품 보유 내역
        joined = JoinedProduct.objects.filter(user=user).select_related("option")
        for jp in joined:
            amt   = jp.amount
            rate  = jp.option.rate
            months= jp.option.term_months
            expected_return = amt * float(rate) / 100 * (months / 12)
            holdings.append({
                "type": "product",
                "name": jp.product.name,
                "quantity": 1,
                "current_price": float(amt),
                "profit_rate": round((expected_return / amt * 100), 2),
            })
            total_invested += amt
            total_profit   += expected_return

        # 4) 요약
        overall_rate = (total_profit / total_invested * 100) if total_invested else 0
        summary = {
            "cash_balance": cash,
            "total_invested": round(total_invested, 2),
            "overall_profit_rate": round(overall_rate, 2),
        }

        # 5) 최근 거래 5건
        trades_qs = VirtualTrade.objects.filter(
            portfolio=portfolio
        ).order_by("-traded_at")[:5]
        recent_trades = []
        for t in trades_qs:
            recent_trades.append({
                "trade_type": t.trade_type,
                "stock_code": t.stock_code,
                "quantity": t.quantity,
                "price": t.price,
                "traded_at": t.traded_at,
                "strategy": t.strategy_run.strategy.name if t.strategy_run else None,
            })

        # 6) 전략 요약
        strat_count = Strategy.objects.filter(user=user).count()
        avg_ret     = StrategyRun.objects.filter(
            strategy__user=user, total_return__isnull=False
        ).aggregate(avg=Avg("total_return"))["avg"] or 0
        best_run    = StrategyRun.objects.filter(
            strategy__user=user, total_return__isnull=False
        ).order_by("-total_return").first()
        strategies = {
            "count": strat_count,
            "average_return": round(float(avg_ret), 2),
            "best_strategy": best_run.strategy.name if best_run else None,
        }

        # 7) 금융상품 추천 (미가입 상품 중 2개 랜덤)
        from financial_products.models import FinancialProduct
        subscribed_ids = [jp.product.id for jp in joined]
        unsub = FinancialProduct.objects.exclude(id__in=subscribed_ids)
        recs = random.sample(list(unsub), min(2, unsub.count()))
        from financial_products.api.serializers import FinancialProductSerializer
        rec_serializer = FinancialProductSerializer(recs, many=True)

        # 직렬화
        data = {
            "summary": DashboardSummarySerializer(summary).data,
            "holdings": HoldingSerializer(holdings, many=True).data,
            "recent_trades": TradeSerializer(recent_trades, many=True).data,
            "strategies": StrategySummarySerializer(strategies).data,
            "recommendations": rec_serializer.data,
        }
        return Response(data)
