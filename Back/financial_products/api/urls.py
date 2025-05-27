# financial_products/api/urls.py
from django.urls import path
from .views import ProductListView, ProductDetailView, ProductJoinView # ProductDetailView 추가

urlpatterns = [
    path("list/", ProductListView.as_view(), name="product-list"),
    path("<str:fin_prdt_cd>/", ProductDetailView.as_view(), name="product-detail"), # ★ 신규 추가 (상품 상세)
    path("join/", ProductJoinView.as_view(), name="product-join"),
    # path("subscribed/", SubscribedProductsListView.as_view(), name="product-subscribed-list"), # (선택적)
]