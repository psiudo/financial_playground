# Back/simulator/api/urls.py
from django.urls import path
from .views import PortfolioView, TradeView

urlpatterns = [
    path("portfolio/", PortfolioView.as_view(), name="sim-portfolio"),
    path("trade/", TradeView.as_view(), name="sim-trade"),
]
