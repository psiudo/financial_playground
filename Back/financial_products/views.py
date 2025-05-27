# Back/financial_products/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import FinancialProduct
from .serializers import FinancialProductSerializer
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FinancialProduct
from .serializers import FinancialProductSerializer

# 🔹 가입한 상품 조회 API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscribed_products(request):
    products = request.user.subscribed_products.all()
    data = [
        {
            "product_id": product.product_id,
            "name": product.name,
            "institution": product.institution,
            "interest_rates": product.interest_rates,
        }
        for product in products
    ]
    return Response(data)


# 🔹 함수형: 상품 가입 API (사용 안 하면 제거 가능)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_product(request, product_id):
    product = get_object_or_404(FinancialProduct, product_id=product_id)
    request.user.subscribed_products.add(product)
    return Response({"message": "가입 완료"})


# 🔹 클래스형: 금융상품 전체 조회
class ProductListView(APIView):
    def get(self, request):
        products = FinancialProduct.objects.all()
        serializer = FinancialProductSerializer(products, many=True)
        return Response(serializer.data)


# 🔹 클래스형: 금융상품 상세 조회
class ProductDetailView(APIView):
    def get(self, request, product_id):
        product = FinancialProduct.objects.filter(product_id=product_id).first()
        if not product:
            return Response({'error': '상품 없음'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FinancialProductSerializer(product)
        return Response(serializer.data)


# 🔹 클래스형: 상품 가입 API
class SubscribeProductView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = FinancialProduct.objects.filter(product_id=product_id).first()
        if not product:
            return Response({'error': '상품 없음'}, status=status.HTTP_404_NOT_FOUND)
        request.user.subscribed_products.add(product)
        return Response({'message': '가입 완료'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_products(request):
    subscribed = request.user.subscribed_products.all()
    unsubscribed = FinancialProduct.objects.exclude(id__in=subscribed)

    # 추천 가능한 상품이 없으면 빈 리스트 반환
    if unsubscribed.count() == 0:
        return Response([], status=200)

    recommendations = random.sample(list(unsubscribed), min(2, unsubscribed.count()))
    serializer = FinancialProductSerializer(recommendations, many=True)
    return Response(serializer.data)


class SubscribeProductView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = FinancialProduct.objects.filter(product_id=product_id).first()
        if not product:
            return Response({'error': '상품 없음'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if product in user.subscribed_products.all():
            return Response({'message': '이미 가입된 상품입니다'}, status=400)

        user.subscribed_products.add(product)
        user.points += 10  # ✅ 포인트 적립
        user.save()        # ✅ 변경사항 저장

        return Response({'message': '가입 완료, 10포인트 적립되었습니다'})
