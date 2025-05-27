# api/serializers.py

from rest_framework import serializers
from insight.models import InterestStock, StockAnalysis, Comment

class InterestStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestStock
        fields = ['id', 'company_name', 'stock_code', 'created_at']

class StockAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAnalysis
        fields = ['id', 'summary', 'keywords', 'sentiment_stats', 'batch_ready']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'likes', 'written_at', 'sentiment']
