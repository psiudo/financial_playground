# Back/notifications/api/serializers.py
from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = [
            "id",
            "noti_type",
            "verb",
            "target",
            "message",
            "link",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields
