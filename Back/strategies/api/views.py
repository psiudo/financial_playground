# Back/strategies/api/views.py
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from strategies.models import Strategy, StrategyRun, StrategyTrade
from .serializers import (
    StrategySerializer, StrategyRunSerializer, StrategyTradeSerializer
)

class StrategyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StrategySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        현재 요청을 보낸 사용자의 전략만 반환합니다.
        """
        return Strategy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StrategyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StrategySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        현재 요청을 보낸 사용자의 전략만 반환합니다.
        """
        # Retrieve, Update, Destroy 시에도 해당 사용자의 전략인지 확인
        return Strategy.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # get_object가 이미 queryset을 통해 권한 검사를 하므로, 여기서 중복 검사할 필요는 없습니다.
        # 다만, 만약의 경우를 대비해 명시적으로 확인할 수 있습니다.
        if serializer.instance.user != self.request.user:
            raise PermissionDenied('본인 전략만 수정할 수 있습니다.')
        serializer.save()

    def perform_destroy(self, instance):
        # get_object가 이미 queryset을 통해 권한 검사를 하므로, 여기서 중복 검사할 필요는 없습니다.
        if instance.user != self.request.user:
            raise PermissionDenied('본인 전략만 삭제할 수 있습니다.')
        instance.delete()

class StrategyRunListAPIView(generics.ListAPIView):
    serializer_class = StrategyRunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 해당 전략이 현재 사용자의 소유인지 먼저 확인
        strategy_pk = self.kwargs['pk']
        strategy = generics.get_object_or_404(Strategy, pk=strategy_pk, user=self.request.user)
        return StrategyRun.objects.filter(strategy=strategy)

class StrategyTradeListAPIView(generics.ListAPIView):
    serializer_class = StrategyTradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 해당 실행이 현재 사용자의 전략에 속하는 실행인지 확인
        run_pk = self.kwargs['run_pk']
        run = generics.get_object_or_404(StrategyRun, pk=run_pk, strategy__user=self.request.user)
        return StrategyTrade.objects.filter(run=run)