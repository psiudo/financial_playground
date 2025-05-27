# Back/financial_products/api/serializers.py

from rest_framework import serializers
from financial_products.models import (
    Bank,
    FinancialProduct,
    ProductOption,
    JoinedProduct,
)
from accounts.models import PointTransaction # 이미 존재


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["code", "name"]


class ProductOptionSerializer(serializers.ModelSerializer): # ★ 수정됨
    class Meta:
        model = ProductOption
        fields = [
            "id",
            "intr_rate_type",       # 이자율 유형 코드 (S:단리, M:복리)
            "intr_rate_type_nm",    # 이자율 유형명
            "rsrv_type",            # 적립 유형 코드 (S:정액, F:자유 - 적금용)
            "rsrv_type_nm",         # 적립 유형명 (적금용)
            "save_trm",             # 저축 기간 (개월) - 현재 CharField
            "intr_rate",            # 저축 금리 (기본)
            "intr_rate2",           # 최고 우대 금리
        ]


class FinancialProductSerializer(serializers.ModelSerializer): # ★ 수정됨
    bank = BankSerializer(read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FinancialProduct
        # API 응답에 포함될 FinancialProduct의 전체 필드 명시
        fields = [
            "id",
            "bank",
            "fin_prdt_cd",          # 금융상품 코드
            "dcls_month",           # 공시월
            "name",                 # 금융상품명
            "product_type",         # 상품 유형 (예금/적금)
            "join_way",             # 가입 방법
            "mtrt_int",             # 만기 후 이자율 설명
            "spcl_cnd",             # 우대 조건
            "join_deny",            # 가입 제한
            "join_member",          # 가입 대상
            "etc_note",             # 기타 유의사항
            "max_limit",            # 최고 한도
            "dcls_strt_day",        # 공시 시작일
            "dcls_end_day",         # 공시 종료일
            "fin_co_subm_day",      # 금융회사 제출일
            "options",              # 수정된 ProductOptionSerializer 사용
            "created_at",           # (선택적)
            "updated_at",           # (선택적)
        ]


class JoinedProductCreateSerializer(serializers.Serializer): # 기존 코드 유지
    option_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate(self, data):
        user = self.context["request"].user
        option_id = data["option_id"]
        # amount = data["amount"] # JoinedProductCreateSerializer에는 amount가 없음. 필요시 추가

        try:
            option = ProductOption.objects.select_related("product", "product__bank").get(
                pk=option_id
            )
        except ProductOption.DoesNotExist:
            raise serializers.ValidationError("선택한 옵션이 존재하지 않습니다")

        # 포인트 잔액 검사 (현재 코드에는 없으나, 필요시 주석 해제 또는 로직 추가)
        # if user.point_balance < amount:
        #     raise serializers.ValidationError("포인트가 부족합니다")

        data["option"] = option
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        option = validated_data["option"]
        amount = validated_data["amount"] # validate에서 amount를 data에 넣지 않았으므로 여기서도 가져와야함.

        from django.db import transaction
        # from django.db.models import F # F객체는 포인트 차감 로직이 현재 없으므로 주석 처리

        with transaction.atomic():
            # 포인트 차감 로직 (현재 코드에는 없으나, 필요시 주석 해제 또는 로직 추가)
            # user.point_balance = F("point_balance") - amount
            # user.save(update_fields=["point_balance"])
            # user.refresh_from_db(fields=["point_balance"])

            # PointTransaction.objects.create(
            #     user=user,
            #     delta_point=-amount,
            #     kind=PointTransaction.DECREASE,
            #     reason="product_join",
            # )

            joined = JoinedProduct.objects.create(
                user=user,
                product=option.product,
                option=option,
                amount=amount, # 이 부분은 JoinedProductCreateSerializer의 필드에 amount가 있어야 함
            )
        return joined

# (선택) 가입된 상품 조회를 위한 Serializer
class JoinedProductSerializer(serializers.ModelSerializer):
    product = FinancialProductSerializer(read_only=True) # 상품 상세 정보 포함
    option = ProductOptionSerializer(read_only=True) # 옵션 상세 정보 포함

    class Meta:
        model = JoinedProduct
        fields = ['id', 'user', 'product', 'option', 'amount', 'joined_at']




class BriefFinancialProductSerializer(serializers.ModelSerializer): # 프로필용 간략한 상품 정보
    bank = BankSerializer(read_only=True)
    class Meta:
        model = FinancialProduct
        fields = ['id', 'name', 'product_type', 'bank']

class BriefProductOptionSerializer(serializers.ModelSerializer): # 프로필용 간략한 옵션 정보
    class Meta:
        model = ProductOption
        fields = ['id', 'save_trm', 'intr_rate', 'intr_rate2', 'intr_rate_type_nm']

class ProfileJoinedProductSerializer(serializers.ModelSerializer):
    product = BriefFinancialProductSerializer(read_only=True)
    option = BriefProductOptionSerializer(read_only=True)

    class Meta:
        model = JoinedProduct
        fields = ['id', 'product', 'option', 'amount', 'joined_at']