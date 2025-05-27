# back/insight/api/urls.py
from django.urls import path
from .views import (
    InterestStockListCreateView,
    InterestStockDetailView,
    AnalyzeTriggerView,
    AnalysisResultView,
)

urlpatterns = [
    path("stocks/", InterestStockListCreateView.as_view(), name="insight-stock-list"),
    path("stocks/<int:pk>/", InterestStockDetailView.as_view(), name="insight-stock-detail"),
    path("<int:pk>/analyze/", AnalyzeTriggerView.as_view(), name="insight-analyze"),
    path("<int:pk>/result/", AnalysisResultView.as_view(), name="insight-result"),
]
