# back/strategies/api/views.py
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from strategies.models import Strategy, StrategyRun, StrategyTrade
from .serializers import (
    StrategySerializer, StrategyRunSerializer, StrategyTradeSerializer
)

class StrategyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StrategyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied('본인 전략만 수정할 수 있습니다')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('본인 전략만 삭제할 수 있습니다')
        instance.delete()

class StrategyRunListAPIView(generics.ListAPIView):
    serializer_class = StrategyRunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StrategyRun.objects.filter(strategy_id=self.kwargs['pk'])

class StrategyTradeListAPIView(generics.ListAPIView):
    serializer_class = StrategyTradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StrategyTrade.objects.filter(run_id=self.kwargs['run_pk'])
