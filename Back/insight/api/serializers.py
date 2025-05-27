# back/insight/api/serializers.py
from rest_framework import serializers
from insight.models import InterestStock, StockAnalysis


class InterestStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestStock
        fields = ["id", "company_name", "stock_code", "created_at"]


class StockAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAnalysis
        fields = [
            "id",
            "summary",
            "keywords",
            "sentiment_stats",
            "task_status",
            "updated_at",
        ]
