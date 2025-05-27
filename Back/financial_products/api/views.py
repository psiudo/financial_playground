# Back/financial_products/api/views.py
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.db.models import Prefetch
from financial_products.models import FinancialProduct, ProductOption, Bank
from .serializers import (
    FinancialProductSerializer,
    JoinedProductCreateSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, ChoiceFilter

# =====================================================================================
# ★★★★★ 중요: recommender.py 파일 위치에 따른 import 경로 확인 ★★★★★
# recommender.py 파일이 financial_products 앱 루트에 있다고 가정 (Back/financial_products/recommenders.py)
from ..recommenders import get_advanced_recommendations # ★ 경로 확인!
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
# ★★★ ProductRecommendationView 원래 로직으로 복구 및 로깅 강화 ★★★
# =====================================================================================
class ProductRecommendationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        logger.info(f"========== ProductRecommendationView GET method CALLED by user: {request.user.username} ==========")
        user = request.user 
        
        raw_recommendations = None 
        try:
            logger.info(f"Attempting to get advanced recommendations for user: {user.username}")
            raw_recommendations = get_advanced_recommendations(user, top_n=5) 
            logger.info(f"Raw recommendations received (count: {len(raw_recommendations) if raw_recommendations is not None else 'None'}): {raw_recommendations}")

            if raw_recommendations is None: 
                logger.error(f"get_advanced_recommendations returned None for user {user.username}")
                # 프론트엔드에서 needsProfileUpdate를 처리할 수 있도록 메시지 조정 가능성 고려
                # 또는 특정 조건 (예: user.risk_grade가 없음)에 따라 다른 메시지 전달
                return Response({
                    "message": "추천 상품 데이터를 가져오지 못했습니다 (recommender returned None). 프로필 정보를 확인해주세요.",
                    "recommended_products": [],
                    "is_fallback": False,
                    "needsProfileUpdate": True # 프로필 정보 부족 가능성 전달
                }, status=status.HTTP_200_OK) # 에러 대신 빈 결과와 메시지로 처리

            results = []
            if raw_recommendations: 
                logger.info(f"Processing {len(raw_recommendations)} raw recommendations.")
                for i, rec_item in enumerate(raw_recommendations):
                    logger.debug(f"Processing recommendation item #{i+1}: {rec_item}")
                    product_instance = rec_item.get('product')
                    if product_instance:
                        try:
                            product_data = FinancialProductSerializer(product_instance).data
                            product_data['recommendation_score'] = rec_item.get('score')
                            product_data['recommendation_reason'] = rec_item.get('reason')
                            results.append(product_data)
                            logger.debug(f"Successfully serialized item #{i+1}: {product_data.get('name')}")
                        except Exception as ser_e:
                            logger.error(f"Serialization error for product ID {product_instance.id if product_instance else 'N/A'}: {ser_e}", exc_info=True)
                    else:
                        logger.warning(f"Recommendation item #{i+1} for user {user.username} did not contain a 'product' instance: {rec_item}")
            
            # is_fallback_applied는 get_advanced_recommendations 내부에서 결정된 값을 사용하거나, 여기서 로직으로 판단
            # 예시: raw_recommendations의 각 아이템에 'is_fallback_item': True/False 플래그가 있다면 그것을 활용
            # 여기서는 전체 결과가 fallback인지 여부를 나타내는 is_fallback을 사용한다고 가정
            # get_advanced_recommendations의 반환값에 is_fallback 여부가 포함되어 있다면 그 값을 사용
            # 여기서는 임시로 결과 개수가 top_n 보다 적으면 fallback으로 간주 (실제 로직에 맞게 수정 필요)
            # 혹은 recommender가 {'recommendations': [...], 'was_fallback': True} 같은 구조로 반환할 수도 있음
            
            # recommender가 반환하는 구조에 따라 is_fallback 설정
            # 현재 get_advanced_recommendations는 추천 리스트만 반환하므로, is_fallback은 여기서 추론해야 함
            # 예를 들어, 최종 결과가 top_n보다 적으면 fallback으로 간주할 수 있지만,
            # 이는 recommender 내부의 fallback 로직이 어떻게 동작하는지에 따라 달라짐.
            # 여기서는 단순히 결과 유무와 메시지로만 전달
            
            final_message = "상품 추천 목록입니다."
            if not results:
                # recommender에서 빈 리스트를 반환했을 때, 프로필 업데이트가 필요한지 여부를 판단해야 함
                if not user.risk_grade or not user.birth_date:
                    final_message = '맞춤 추천을 받으려면 프로필에서 투자 성향과 생년월일을 먼저 입력해주세요.'
                    needs_profile_update = True
                else:
                    final_message = '현재 조건에 맞는 추천 상품을 찾지 못했습니다.'
                    needs_profile_update = False
            else:
                needs_profile_update = False


            logger.info(f"Successfully processed {len(results)} recommendations for user {user.username}.")
            return Response({
                "message": final_message,
                "recommended_products": results,
                "is_fallback": False, # 이 값은 recommender.py에서 결정되어 전달되거나 여기서 추론해야 합니다.
                                     # 현재는 프론트엔드가 자체적으로 판단하도록 False로 설정.
                "needsProfileUpdate": needs_profile_update # 프로필 업데이트 필요 여부 전달
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unhandled error in ProductRecommendationView for user {user.username}: {e}", exc_info=True)
            logger.error(f"State of raw_recommendations when error occurred: {raw_recommendations}") 
            return Response(
                {"message": "추천 상품을 가져오는 중 심각한 서버 오류가 발생했습니다.", "error_details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# =====================================================================================