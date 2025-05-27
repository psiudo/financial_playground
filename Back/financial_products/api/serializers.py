# back/financial_products/api/serializers.py
from rest_framework import serializers
from financial_products.models import (
    Bank,
    FinancialProduct,
    ProductOption,
    JoinedProduct,
)
from accounts.models import PointTransaction


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["code", "name"]


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ["id", "term_months", "rate"]


class FinancialProductSerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = FinancialProduct
        fields = ["id", "bank", "name", "product_type", "description", "options"]


class JoinedProductCreateSerializer(serializers.Serializer):
    """
    POST /api/products/join/ 에서 사용
    """
    option_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate(self, data):
        user = self.context["request"].user
        option_id = data["option_id"]
        amount = data["amount"]

        try:
            option = ProductOption.objects.select_related("product", "product__bank").get(
                pk=option_id
            )
        except ProductOption.DoesNotExist:
            raise serializers.ValidationError("선택한 옵션이 존재하지 않습니다")

        # 포인트 잔액 검사 (1포인트 = 1원 가정)
        if user.point_balance < amount:
            raise serializers.ValidationError("포인트가 부족합니다")

        data["option"] = option
        return data

    def create(self, validated_data):
        """
        JoinedProduct 저장 + PointTransaction 차감
        """
        user = self.context["request"].user
        option = validated_data["option"]
        amount = validated_data["amount"]

        # 포인트 차감 및 JoinedProduct 생성
        from django.db import transaction
        from django.db.models import F

        with transaction.atomic():
            user.point_balance = F("point_balance") - amount
            user.save(update_fields=["point_balance"])
            user.refresh_from_db(fields=["point_balance"])

            PointTransaction.objects.create(
                user=user,
                delta_point=-amount,
                kind=PointTransaction.DECREASE,
                reason="product_join",
            )

            joined = JoinedProduct.objects.create(
                user=user,
                product=option.product,
                option=option,
                amount=amount,
            )
        return joined
