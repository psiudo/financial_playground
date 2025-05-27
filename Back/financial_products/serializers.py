# financial_products/serializers.py

from rest_framework import serializers
from .models import FinancialProduct

class FinancialProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialProduct
        fields = '__all__'
