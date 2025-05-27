# back/notifications/api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from .serializers import NotificationSerializer
from notifications.models import Notification


class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/      → 내 알림 전체
    GET ...?unread=true          → 읽지 않은 것만
    """
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get("unread") == "true":
            qs = qs.filter(is_read=False)
        return qs


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def notification_mark_read(request, pk: int):
    """
    POST /api/notifications/<pk>/read/  → 단건 읽음 처리
    """
    obj = get_object_or_404(Notification, pk=pk, user=request.user)
    if not obj.is_read:
        obj.is_read = True
        obj.save(update_fields=["is_read"])
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def notification_mark_all_read(request):
    """
    POST /api/notifications/read-all/   → 전체 읽음 처리
    """
    qs = Notification.objects.filter(user=request.user, is_read=False)
    qs.update(is_read=True)
    return Response(status=status.HTTP_204_NO_CONTENT)
