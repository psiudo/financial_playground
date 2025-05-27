# back/api/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from insight.models import InterestStock, StockAnalysis, Comment
from .serializers import InterestStockSerializer, StockAnalysisSerializer, CommentSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interest_stocks(request):
    stocks = InterestStock.objects.filter(user=request.user)
    serializer = InterestStockSerializer(stocks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_analysis(request, stock_id):
    try:
        analysis = StockAnalysis.objects.get(stock__id=stock_id)
    except StockAnalysis.DoesNotExist:
        return Response({"error": "분석 정보가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StockAnalysisSerializer(analysis)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_comments(request, stock_id):
    comments = Comment.objects.filter(analysis__stock__id=stock_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)
