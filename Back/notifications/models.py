# back/notifications/models.py
from django.db import models
from django.conf import settings


class Notification(models.Model):
    # 알림 범주
    TRADE      = "trade"
    PRODUCT    = "product"
    STRATEGY   = "strategy"
    COMMUNITY  = "community"
    SYSTEM     = "system"

    TYPE_CHOICES = [
        (TRADE,     "거래"),
        (PRODUCT,   "금융상품"),
        (STRATEGY,  "전략"),
        (COMMUNITY, "커뮤니티"),
        (SYSTEM,    "시스템"),
    ]

    # 핵심 필드
    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    noti_type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default=SYSTEM)
    verb       = models.CharField(max_length=50)              # 예: "새 글 작성"
    target     = models.CharField(max_length=100, blank=True) # 예: "post:15"
    message    = models.CharField(max_length=255, blank=True)
    link       = models.URLField(blank=True)

    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.verb}] {self.message}"
