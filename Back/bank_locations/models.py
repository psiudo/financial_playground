# Back/bank_locations/models.py
from django.db import models
from django.conf import settings


class BankBranch(models.Model):
    bank_name   = models.CharField(max_length=100)        # xy은행
    branch_name = models.CharField(max_length=150)        # ab지점
    address     = models.CharField(max_length=255)
    latitude    = models.DecimalField(max_digits=9, decimal_places=6)
    longitude   = models.DecimalField(max_digits=9, decimal_places=6)
    phone       = models.CharField(max_length=20, blank=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("bank_name", "branch_name", "address")

    def __str__(self):
        return f"{self.bank_name} {self.branch_name}"
