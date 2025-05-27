# simulator/urls.py

from django.urls import path
from . import views 

urlpatterns = [
    path('portfolio/', views.my_portfolio, name='my_portfolio'),
    path('buy/', views.buy_stock, name='buy_stock'),
    path('sell/<int:trade_id>/', views.sell_stock, name='sell_stock'),
    path('history/', views.trade_history, name='trade_history'),

    # DRF 기반 API
    path('api/portfolio/', views.MyPortfolioAPI.as_view()),
    path('api/buy/', views.BuyStockAPI.as_view()),
    path('api/sell/<int:trade_id>/', views.SellStockAPI.as_view()),
    path('api/history/', views.TradeHistoryAPI.as_view()),
    path('api/profit-rate/', views.ProfitRateAPI.as_view()), 
]
