# Back/strategies/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    # path('portfolio/', views.my_portfolio, name='my_portfolio'),
    # path('buy/', views.buy_stock, name='buy_stock'),
    # path('sell/<int:trade_id>/', views.sell_stock, name='sell_stock'),
    # path('history/', views.trade_history, name='trade_history'),

    # # DRF 기반 API
    # path('api/portfolio/', views.MyPortfolioAPI.as_view()),
    # path('api/buy/', views.BuyStockAPI.as_view()),
    # path('api/sell/<int:trade_id>/', views.SellStockAPI.as_view()),
    # path('api/history/', views.TradeHistoryAPI.as_view()),
    # path('api/profit-rate/', views.ProfitRateAPI.as_view()),
    # path('api/stock-info/', views.StockInfoAPI.as_view()),
    # path('api/stock-price/', views.StockPriceAPI.as_view()),
    # path('api/stock-chart/', views.StockChartAPI.as_view()),
    # path('api/stock-news/', views.StockNewsAPI.as_view()), 
    # path('api/stock-recommendations/', views.StockRecommendationsAPI.as_view()),
    # path('api/stock-analytics/', views.StockAnalyticsAPI.as_view()),
    # path('api/stock-alerts/', views.StockAlertsAPI.as_view()),
    # path('api/stock-portfolio/', views.StockPortfolioAPI.as_view()),
    # path('api/stock-portfolio-history/', views.StockPortfolioHistoryAPI.as_view()),
    # path('api/stock-portfolio-performance/', views.StockPortfolioPerformanceAPI.as_view()),
    # path('api/stock-portfolio-risk/', views.StockPortfolioRiskAPI.as_view()),
    # path('api/stock-portfolio-optimization/', views.StockPortfolioOptimizationAPI.as_view()),
    # path('api/stock-portfolio-rebalancing/', views.StockPortfolioRebalancingAPI.as_view()),
]