# Back/insight/api/serializers.py
from rest_framework import serializers
# 변경된 임포트: Stock -> InterestStock
from insight.models import InterestStock, StockAnalysis, Comment 

class InterestStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestStock
        fields = ['id', 'user', 'company_name', 'stock_code', 'created_at'] 
        # user 필드는 username 등으로 표현하고 싶다면 추가 설정 필요
        # 예: user = serializers.StringRelatedField() 또는 커스텀 SerializerMethodField

class StockAnalysisSerializer(serializers.ModelSerializer):
    # StockAnalysis 모델의 'stock' 필드가 InterestStock을 가리키므로, InterestStockSerializer를 사용
    stock = InterestStockSerializer(read_only=True) 
    # 기존 필드명과 새 모델의 필드명 매칭:
    # summary -> summary (동일)
    # keywords -> keywords (동일)
    # sentiment_stats -> sentiment_stats (동일)
    # batch_ready -> batch_ready (동일)
    # task_status -> task_status (동일)
    # updated_at -> updated_at (동일)
    # overall_sentiment 필드가 StockAnalysis 모델에 없음 -> 추가하거나, sentiment_stats에서 계산하여 제공
    # last_analyzed_at -> updated_at 필드로 대체 가능 (의미상 유사)

    # overall_sentiment를 위한 SerializerMethodField (선택적)
    overall_sentiment_display = serializers.SerializerMethodField()

    class Meta:
        model = StockAnalysis
        fields = [
            'stock', 
            'summary', 
            'keywords', 
            'sentiment_stats', 
            'batch_ready', 
            'task_status', 
            'updated_at', # last_analyzed_at 대신 사용
            'overall_sentiment_display' # 추가된 필드
        ]

    def get_overall_sentiment_display(self, obj):
        # sentiment_stats를 기반으로 overall_sentiment를 계산하거나,
        # StockAnalysis 모델에 overall_sentiment 필드를 추가하고 그 값을 반환
        # 예시: sentiment_stats에 'positive', 'negative', 'neutral' 카운트가 있다고 가정
        stats = obj.sentiment_stats
        if not stats or not isinstance(stats, dict):
            return "N/A"
        
        positive = stats.get('positive', 0)
        negative = stats.get('negative', 0)
        # neutral = stats.get('neutral', 0) # 모델 필드에 따라
        
        if positive > negative:
            return "긍정적"
        elif negative > positive:
            return "부정적"
        else: # positive == negative 또는 둘 다 0
            return "중립적"


class CommentSerializer(serializers.ModelSerializer):
    analysis = serializers.StringRelatedField() # StockAnalysis 객체의 문자열 표현
    class Meta:
        model = Comment
        fields = ['id', 'analysis', 'author', 'content', 'sentiment', 'likes', 'written_at']