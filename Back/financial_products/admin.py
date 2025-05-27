# back/financial_products/admin.py
from django.contrib import admin
from .models import Bank, FinancialProduct, ProductOption, JoinedProduct


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(FinancialProduct)
class FinancialProductAdmin(admin.ModelAdmin):
    list_display  = ("name", "bank", "product_type", "created_at")
    list_filter   = ("product_type", "bank")
    search_fields = ("name",)


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display  = ("product", "term_months", "rate")
    list_filter   = ("term_months", "product")


@admin.register(JoinedProduct)
class JoinedProductAdmin(admin.ModelAdmin):
    list_display  = ("user", "product", "option", "amount", "joined_at")
    list_filter   = ("product", "option", "joined_at")
    search_fields = ("user__username",)
