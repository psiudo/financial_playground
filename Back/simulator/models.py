# back/simulator/models.py
from django.db import models
from django.conf import settings


class VirtualPortfolio(models.Model):
    user          = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cash_balance  = models.BigIntegerField(default=10_000_000)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Portfolio"


class VirtualTrade(models.Model):
    BUY  = "buy"
    SELL = "sell"
    TRADE_CHOICES = [(BUY, "매수"), (SELL, "매도")]

    portfolio   = models.ForeignKey(VirtualPortfolio, on_delete=models.CASCADE, related_name="trades")
    trade_type  = models.CharField(max_length=4, choices=TRADE_CHOICES)
    stock_code  = models.CharField(max_length=12)
    stock_name  = models.CharField(max_length=100)
    price       = models.PositiveIntegerField()
    quantity    = models.PositiveIntegerField()
    traded_at   = models.DateTimeField(auto_now_add=True)
    strategy_run = models.ForeignKey("strategies.StrategyRun", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-traded_at"]

    def __str__(self):
        return f"{self.portfolio.user.username} {self.trade_type} {self.stock_code}"
