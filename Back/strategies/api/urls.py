# back/strategies/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('strategies/', views.StrategyListCreateAPIView.as_view(), name='strategy-list-create'),
    path('strategies/<int:pk>/', views.StrategyRetrieveUpdateDestroyAPIView.as_view(), name='strategy-detail'),
    path('strategies/<int:pk>/runs/', views.StrategyRunListAPIView.as_view(), name='strategy-run-list'),
    path('runs/<int:run_pk>/trades/', views.StrategyTradeListAPIView.as_view(), name='run-trade-list'),
]
