# Back/insight/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from insight.models import InterestStock, StockAnalysis
from .serializers import (
    InterestStockSerializer,
    StockAnalysisResultSerializer,
)
from django.conf import settings
from insight.tasks import run_analysis_task


class InterestStockListCreateView(generics.ListCreateAPIView):
    """
    관심 종목 리스트 조회·추가
    GET /api/insight/stocks/
    POST /api/insight/stocks/
    """
    serializer_class = InterestStockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InterestStock.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InterestStockDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    관심 종목 단건 조회·수정·삭제
    """
    serializer_class = InterestStockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InterestStock.objects.filter(user=self.request.user)


class AnalyzeTriggerView(generics.GenericAPIView):
    """
    POST /api/insight/<pk>/analyze/
    Celery 태스크 지연 실행
    """
    permission_classes = [permissions.IsAuthenticated]

# AnalyzeTriggerView 내부 post 메서드
    def post(self, request, pk):
        stock = get_object_or_404(InterestStock, pk=pk, user=request.user)
        analysis, _ = StockAnalysis.objects.get_or_create(stock=stock)

        if analysis.task_status == StockAnalysis.RUNNING:
            return Response(
                {"detail": "이미 분석 중입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Celery 사용 여부 결정
        use_celery = getattr(settings, "USE_CELERY", False)
        if use_celery:
            run_analysis_task.delay(analysis.id)
            analysis.task_status = StockAnalysis.RUNNING
            analysis.save(update_fields=["task_status"])
            return Response(
                {"detail": "분석을 백그라운드에서 시작했습니다"},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            run_analysis_task(analysis.id)  # 직접 호출
            return Response(
                {"detail": "분석이 완료되었습니다"},
                status=status.HTTP_200_OK,
            )



class AnalysisResultView(generics.RetrieveAPIView):
    """
    GET /api/insight/<pk>/result/
    분석 결과 반환
    """
    serializer_class = StockAnalysisResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        stock = get_object_or_404(InterestStock, pk=self.kwargs["pk"], user=self.request.user)
        analysis = get_object_or_404(StockAnalysis, stock=stock)
        return analysis
