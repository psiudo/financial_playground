# back/financial_products/models.py
from django.db import models
from django.conf import settings


class Bank(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FinancialProduct(models.Model):
    DEPOSIT = "deposit"
    SAVING  = "saving"
    TYPE_CHOICES = [(DEPOSIT, "정기예금"), (SAVING, "적금")]

    bank         = models.ForeignKey(Bank, on_delete=models.CASCADE)
    name         = models.CharField(max_length=150)
    product_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description  = models.TextField(blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("bank", "name")

    def __str__(self):
        return f"{self.bank.name} {self.name}"


class ProductOption(models.Model):
    product     = models.ForeignKey(FinancialProduct, on_delete=models.CASCADE, related_name="options")
    term_months = models.PositiveSmallIntegerField()
    rate        = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ("product", "term_months")

    def __str__(self):
        return f"{self.product.name} {self.term_months}개월"


class JoinedProduct(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product   = models.ForeignKey(FinancialProduct, on_delete=models.CASCADE)
    option    = models.ForeignKey(ProductOption, on_delete=models.PROTECT)
    amount    = models.PositiveIntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product", "option")

    def __str__(self):
        return f"{self.user.username} {self.product.name}"
