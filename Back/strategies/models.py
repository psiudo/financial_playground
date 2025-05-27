# strategies/models.py
from django.db import models
from django.conf import settings


class Strategy(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name        = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    rule_json   = models.JSONField()
    is_public   = models.BooleanField(default=False)
    is_paid     = models.BooleanField(default=False)
    price_point = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.user.username} {self.name}"


class StrategyRun(models.Model):
    strategy     = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name="runs")
    started_at   = models.DateTimeField(auto_now_add=True)
    ended_at     = models.DateTimeField(null=True, blank=True)
    total_return = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.strategy.name} run"


class StrategyTrade(models.Model):
    run        = models.ForeignKey(StrategyRun, on_delete=models.CASCADE, related_name="trades")
    stock_code = models.CharField(max_length=12)
    trade_type = models.CharField(max_length=4)      # buy / sell
    price      = models.PositiveIntegerField()
    quantity   = models.PositiveIntegerField()
    traded_at  = models.DateTimeField()

    def __str__(self):
        return f"{self.run.id} {self.stock_code}"
