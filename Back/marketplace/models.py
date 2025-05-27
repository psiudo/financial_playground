# marketplace/models.py
from django.db import models
from django.conf import settings


class MarketListing(models.Model):
    strategy    = models.OneToOneField("strategies.Strategy", on_delete=models.CASCADE)
    seller      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price_point = models.PositiveIntegerField()
    sales       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.strategy.name} {self.price_point}P"


class Purchase(models.Model):
    buyer       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing     = models.ForeignKey(MarketListing, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("buyer", "listing")

    def __str__(self):
        return f"{self.buyer.username} bought {self.listing.strategy.name}"
