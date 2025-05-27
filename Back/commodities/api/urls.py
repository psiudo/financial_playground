# Back/commodities/api/urls.py
from django.urls import path
from .views import CommodityListAPIView, CommodityHistoryAPIView

urlpatterns = [
    # 전체 현물 상품 목록 (최신 가격 포함)
    # GET /api/commodities/list/  <--- 프론트엔드 호출 경로와 일치하도록 수정
    path('list/', CommodityListAPIView.as_view(), name='commodity-list'), 
    
    # 특정 현물 상품의 가격 이력 (기간 필터링 가능)
    # GET /api/commodities/GOLD/history/?from=YYYY-MM-DD&to=YYYY-MM-DD
    path('<str:symbol>/history/', CommodityHistoryAPIView.as_view(), name='commodity-price-history'),
]