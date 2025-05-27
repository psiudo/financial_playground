# commodities/api/urls.py
from django.urls import path
from .views import CommodityListAPIView, CommodityHistoryAPIView

urlpatterns = [
    path("list/", CommodityListAPIView.as_view(), name="commodities-list"),
    path("<str:symbol>/history/", CommodityHistoryAPIView.as_view(), name="commodity-history"),
]
