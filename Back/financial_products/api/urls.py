# back/financial_products/api/urls.py
from django.urls import path
from .views import ProductListView, ProductJoinView

urlpatterns = [
    path("list/", ProductListView.as_view(), name="product-list"),
    path("join/", ProductJoinView.as_view(), name="product-join"),
]
