# back/financial_products/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Prefetch, Q
from django.db import models # <--- 이 줄을 추가해주세요!
from financial_products.models import FinancialProduct, ProductOption, Bank
from .serializers import (
    FinancialProductSerializer,
    JoinedProductCreateSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, ChoiceFilter


class FinancialProductFilter(FilterSet):
    bank_code = CharFilter(field_name='bank__code', lookup_expr='exact')
    bank_name = CharFilter(field_name='bank__name', lookup_expr='icontains')
    product_type = ChoiceFilter(field_name='product_type', choices=FinancialProduct.PRODUCT_TYPE_CHOICES)
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = FinancialProduct
        fields = ['bank_code', 'bank_name', 'product_type', 'name']


class ProductListView(generics.ListAPIView):
    """
    GET /api/financial_products/list/  (주석에서 products -> financial_products로 경로 수정 고려)
    모든 금융상품 + 옵션 목록 반환
    - 필터링: ?bank_code=<code>, ?bank_name=<name>, ?product_type=<type>, ?name=<product_name>
    """
    queryset = (
        FinancialProduct.objects.select_related("bank")
        .prefetch_related(
            Prefetch("options", queryset=ProductOption.objects.order_by('save_trm')) # Cast 없이 직접 정렬
        )
        # .order_by("bank__name", "name") # FilterSet에서 정렬을 다룰 수 있으므로 주석 처리하거나 필요시 유지
    )
    serializer_class = FinancialProductSerializer
    permission_classes = [permissions.AllowAny] 
    filter_backends = [DjangoFilterBackend] 
    filterset_class = FinancialProductFilter


class ProductDetailView(generics.RetrieveAPIView): 
    """
    GET /api/financial_products/<str:fin_prdt_cd>/ (주석에서 products -> financial_products로 경로 수정 고려)
    특정 금융 상품의 상세 정보 (옵션 포함) 반환
    """
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
        remaining_points = request.user.point_balance 
        return Response(
            {
                "message": "상품 가입이 완료되었습니다.", 
                "joined_product_id": joined.id,
                "remaining_point_balance": remaining_points,
            },
            status=status.HTTP_201_CREATED,
        )