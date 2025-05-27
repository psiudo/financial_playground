# simulator/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import VirtualTradeSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VirtualPortfolio, VirtualTrade
from insight.models import InterestStock
from simulator.services.price_service import fetch_current_price

AVAILABLE_STOCKS = [
    '삼성전자',
    'SK하이닉스',
    'LG에너지솔루션',
]

@login_required
def my_portfolio(request):
    portfolio = VirtualPortfolio.objects.get(user=request.user)
    trades = VirtualTrade.objects.filter(portfolio=portfolio)

    for trade in trades:
        trade.current_price = fetch_current_price(trade.stock.company_name)
        total_buy = trade.quantity * trade.price
        total_now = trade.quantity * trade.current_price
        trade.profit_rate = (total_now / total_buy * 100) if total_buy else 0

    return render(request, 'simulator/my_portfolio.html', {
        'portfolio': portfolio,
        'trades': trades,
        'available_stocks': AVAILABLE_STOCKS,
    })

@login_required
def buy_stock(request):
    portfolio, _ = VirtualPortfolio.objects.get_or_create(
        user=request.user,
        defaults={'cash_balance': 10000000}
    )

    if request.method == 'POST':
        stock_name = request.POST.get('stock_name')
        quantity = int(request.POST.get('quantity'))

        try:
            stock_obj = InterestStock.objects.get(company_name=stock_name)
        except InterestStock.DoesNotExist:
            return render(request, 'simulator/buy_stock.html', {
                'error_message': '선택한 종목이 존재하지 않습니다',
                'available_stock_names': AVAILABLE_STOCKS,
            })

        price = fetch_current_price(stock_name)
        total_cost = quantity * price

        if portfolio.cash_balance >= total_cost:
            portfolio.cash_balance -= total_cost
            portfolio.save()

            VirtualTrade.objects.create(
                portfolio=portfolio,
                stock=stock_obj,
                quantity=quantity,
                price=price,
                is_buy=True
            )

            return redirect('simulator:my_portfolio')
        else:
            return render(request, 'simulator/buy_stock.html', {
                'error_message': '현금이 부족합니다.',
                'available_stock_names': AVAILABLE_STOCKS,
            })

    return render(request, 'simulator/buy_stock.html', {
        'available_stock_names': AVAILABLE_STOCKS,
    })

@login_required
def sell_stock(request, trade_id):
    trade = get_object_or_404(VirtualTrade, id=trade_id, portfolio__user=request.user)
    portfolio = trade.portfolio

    if request.method == 'POST':
        sell_price = int(request.POST.get('price'))
        quantity = trade.quantity

        VirtualTrade.objects.create(
            portfolio=portfolio,
            stock=trade.stock,
            quantity=quantity,
            price=sell_price,
            is_buy=False
        )

        portfolio.cash_balance += sell_price * quantity
        portfolio.save()

        trade.delete()

        return redirect('simulator:my_portfolio')

    return redirect('simulator:my_portfolio')

@login_required
def trade_history(request):
    portfolio, _ = VirtualPortfolio.objects.get_or_create(
        user=request.user,
        defaults={'cash_balance': 10000000}
    )

    trades = portfolio.trades.all().order_by('-traded_at')

    return render(request, 'simulator/trade_history.html', {
        'portfolio': portfolio,
        'trades': trades,
    })


class MyPortfolioAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        portfolio, _ = VirtualPortfolio.objects.get_or_create(user=request.user)
        trades = portfolio.trades.all()
        serializer = VirtualTradeSerializer(trades, many=True)
        return Response({
            'cash_balance': portfolio.cash_balance,
            'trades': serializer.data,
        })


class BuyStockAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stock_name = request.data.get('stock_name')
        quantity = int(request.data.get('quantity'))
        try:
            stock_obj = InterestStock.objects.get(company_name=stock_name)
        except InterestStock.DoesNotExist:
            return Response({'error': '종목 없음'}, status=400)

        price = fetch_current_price(stock_name)
        total_cost = quantity * price
        portfolio, _ = VirtualPortfolio.objects.get_or_create(user=request.user)

        if portfolio.cash_balance < total_cost:
            return Response({'error': '현금 부족'}, status=400)

        portfolio.cash_balance -= total_cost
        portfolio.save()

        trade = VirtualTrade.objects.create(
            portfolio=portfolio,
            stock=stock_obj,
            quantity=quantity,
            price=price,
            is_buy=True
        )

        return Response({'message': '매수 성공', 'trade_id': trade.id})


class SellStockAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, trade_id):
        try:
            trade = VirtualTrade.objects.get(id=trade_id, portfolio__user=request.user)
        except VirtualTrade.DoesNotExist:
            return Response({'error': '거래 없음'}, status=404)

        portfolio = trade.portfolio
        sell_price = fetch_current_price(trade.stock.company_name)

        VirtualTrade.objects.create(
            portfolio=portfolio,
            stock=trade.stock,
            quantity=trade.quantity,
            price=sell_price,
            is_buy=False
        )

        portfolio.cash_balance += sell_price * trade.quantity
        portfolio.save()
        trade.delete()

        return Response({'message': '매도 완료'})


class TradeHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        portfolio = VirtualPortfolio.objects.get(user=request.user)
        trades = portfolio.trades.all().order_by('-traded_at')
        serializer = VirtualTradeSerializer(trades, many=True)
        return Response(serializer.data)


class ProfitRateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            portfolio = VirtualPortfolio.objects.get(user=request.user)
        except VirtualPortfolio.DoesNotExist:
            return Response({'error': '포트폴리오 없음'}, status=404)

        trades = portfolio.trades.filter(is_buy=True)
        result = []
        total_profit = 0
        total_invested = 0

        for trade in trades:
            current_price = fetch_current_price(trade.stock.company_name)
            invested = trade.quantity * trade.price
            now_value = trade.quantity * current_price
            profit = now_value - invested
            profit_rate = (profit / invested * 100) if invested else 0

            total_profit += profit
            total_invested += invested

            result.append({
                'company_name': trade.stock.company_name,
                'quantity': trade.quantity,
                'buy_price': float(trade.price),
                'current_price': float(current_price),
                'profit': float(profit),
                'profit_rate': round(profit_rate, 2),
            })

        overall_rate = (total_profit / total_invested * 100) if total_invested else 0

        return Response({
            'total_profit': round(total_profit, 2),
            'total_invested': round(total_invested, 2),
            'overall_rate': round(overall_rate, 2),
            'positions': result
        })