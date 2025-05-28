# Back/financial_products/api/urls.py
from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductJoinView,
    ProductRecommendationView
)

urlpatterns = [
    path("list/", ProductListView.as_view(), name="product-list"),
    path("join/", ProductJoinView.as_view(), name="product-join"),
    path("recommendations/", ProductRecommendationView.as_view(), name="product-recommendations"), # 위로 이동
    path("<str:fin_prdt_cd>/", ProductDetailView.as_view(), name="product-detail"), # 아래로 이동 / 또는 가장 마지막으로
]