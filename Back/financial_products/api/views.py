# Back/financial_products/api/views.py
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.db.models import Prefetch, Q, Max, Min, F, Value, IntegerField, FloatField, CharField, Subquery, OuterRef
from django.db.models.functions import Coalesce, Cast
# from django.utils import timezone # 테스트 중에는 불필요
# from datetime import date # 테스트 중에는 불필요

from financial_products.models import FinancialProduct, ProductOption, Bank
# from accounts.models import CustomUser # 테스트 중에는 불필요
from .serializers import (
    FinancialProductSerializer,
    JoinedProductCreateSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, ChoiceFilter

# =====================================================================================
# ★★★★★ 중요: recommender.py 파일 위치에 따른 import 경로 확인 ★★★★★
# 1. 만약 recommenders.py 파일이 financial_products 앱 루트에 있다면 (Back/financial_products/recommenders.py):
# from ..recommenders import get_advanced_recommendations # 테스트 중에는 주석 처리
# 2. 만약 recommenders.py 파일이 현재 api 폴더 내에 있다면 (Back/financial_products/api/recommenders.py):
# from .recommenders import get_advanced_recommendations # 테스트 중에는 주석 처리
# =====================================================================================
import logging
logger = logging.getLogger(__name__)


class FinancialProductFilter(FilterSet):
    bank_code = CharFilter(field_name='bank__code', lookup_expr='exact')
    bank_name = CharFilter(field_name='bank__name', lookup_expr='icontains')
    product_type = ChoiceFilter(field_name='product_type', choices=FinancialProduct.PRODUCT_TYPE_CHOICES)
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = FinancialProduct
        fields = ['bank_code', 'bank_name', 'product_type', 'name']


class ProductListView(generics.ListAPIView):
    queryset = (
        FinancialProduct.objects.select_related("bank")
        .prefetch_related(
            Prefetch("options", queryset=ProductOption.objects.order_by('save_trm'))
        )
        .filter(bank__isnull=False) 
        .distinct()
    )
    serializer_class = FinancialProductSerializer
    permission_classes = [permissions.AllowAny] 
    filter_backends = [DjangoFilterBackend] 
    filterset_class = FinancialProductFilter


class ProductDetailView(generics.RetrieveAPIView): 
    queryset = FinancialProduct.objects.select_related("bank").prefetch_related(
        Prefetch("options", queryset=ProductOption.objects.order_by('save_trm'))
    )
    serializer_class = FinancialProductSerializer
    permission_classes = [permissions.AllowAny] 
    lookup_field = 'fin_prdt_cd' 


class ProductJoinView(generics.GenericAPIView): 
    serializer_class = JoinedProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        joined = serializer.save()
        return Response(
            {
                "message": "상품 가입이 완료되었습니다.", 
                "joined_product_id": joined.id,
            },
            status=status.HTTP_201_CREATED,
        )
# =====================================================================================
# ★★★ ProductRecommendationView 임시 단순화 ★★★
# =====================================================================================
class ProductRecommendationView(views.APIView): # generics.ListAPIView 대신 views.APIView
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logger.info(f"========== ProductRecommendationView GET method CALLED (SIMPLIFIED TEST) by user: {request.user.username} ==========")
        
        test_data = {
            "message": "This is a SIMPLIFIED TEST response from ProductRecommendationView.",
            "recommended_products": [
                {"fin_prdt_cd": "TEST001", "fin_prdt_nm": "Simplified Test Product 1 (from view)", "bank": {"name": "Test Bank"}, "options": [], "product_type": "deposit", "recommendation_score": 100, "recommendation_reason": "Simplified Test reason 1"},
                {"fin_prdt_cd": "TEST002", "fin_prdt_nm": "Simplified Test Product 2 (from view)", "bank": {"name": "Test Bank"}, "options": [], "product_type": "saving", "recommendation_score": 90, "recommendation_reason": "Simplified Test reason 2"}
            ],
            "is_fallback": False
        }
        return Response(test_data, status=status.HTTP_200_OK)
# =====================================================================================
