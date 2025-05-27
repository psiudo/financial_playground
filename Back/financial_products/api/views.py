# back/financial_products/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Prefetch
from financial_products.models import FinancialProduct, ProductOption
from .serializers import (
    FinancialProductSerializer,
    JoinedProductCreateSerializer,
)


class ProductListView(generics.ListAPIView):
    """
    GET /api/products/list/
    모든 금융상품 + 옵션 목록 반환
    """
    queryset = (
        FinancialProduct.objects.select_related("bank")
        .prefetch_related(
            Prefetch("options", queryset=ProductOption.objects.order_by("term_months"))
        )
        .order_by("bank__name", "name")
    )
    serializer_class = FinancialProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductJoinView(generics.GenericAPIView):
    """
    POST /api/products/join/
    - 필드: option_id, amount
    - JoinedProduct 저장 + 포인트 차감
    """
    serializer_class = JoinedProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        joined = serializer.save()
        return Response(
            {
                "joined_product_id": joined.id,
                "remaining_point_balance": request.user.point_balance,
            },
            status=status.HTTP_201_CREATED,
        )
