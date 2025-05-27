# back/insight/models.py
from django.db import models
from django.conf import settings


class InterestStock(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    stock_code   = models.CharField(max_length=10)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company_name")

    def __str__(self):
        return f"{self.user.username} {self.company_name}"


class StockAnalysis(models.Model):
    WAITING  = "waiting"
    RUNNING  = "running"
    DONE     = "done"
    FAILED   = "failed"
    STATUS_CHOICES = [(WAITING, "대기"), (RUNNING, "진행"), (DONE, "완료"), (FAILED, "실패")]

    stock           = models.OneToOneField(InterestStock, on_delete=models.CASCADE)
    summary         = models.TextField(blank=True)
    keywords        = models.JSONField(default=list, blank=True)
    sentiment_stats = models.JSONField(default=dict, blank=True)
    batch_ready     = models.BooleanField(default=False)
    task_status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default=WAITING)
    updated_at      = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    analysis    = models.ForeignKey(StockAnalysis, on_delete=models.CASCADE, related_name="comments")
    author      = models.CharField(max_length=100)
    content     = models.TextField()
    sentiment   = models.CharField(max_length=10, blank=True)
    likes       = models.PositiveIntegerField(default=0)
    written_at  = models.DateTimeField()

    class Meta:
        ordering = ["-likes"]

    def __str__(self):
        return f"{self.author} {self.content[:15]}"
