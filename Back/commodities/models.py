# commodities/models.py
from django.db import models


class Commodity(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    symbol      = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commodity"
        verbose_name_plural = "Commodities"   # 복수형 직접 지정

    def __str__(self):
        return self.name


class PriceHistory(models.Model):
    commodity  = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, related_name="prices"
    )
    date       = models.DateField()
    price      = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("commodity", "date")
        ordering = ["date"]
        verbose_name = "Price history"
        verbose_name_plural = "Price histories"  # 복수형 직접 지정

    def __str__(self):
        return f"{self.commodity.symbol} {self.date} {self.price}"
