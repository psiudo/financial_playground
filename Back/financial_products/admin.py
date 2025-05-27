# financial_products/admin.py
from django.contrib import admin
from .models import Bank, FinancialProduct, ProductOption, JoinedProduct


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(FinancialProduct)
class FinancialProductAdmin(admin.ModelAdmin):
    list_display  = ("name", "bank", "product_type", "dcls_month", "updated_at") # dcls_month, updated_at 추가하여 정보성 강화
    list_filter   = ("product_type", "bank", "dcls_month") # dcls_month 추가
    search_fields = ("name", "fin_prdt_cd") # fin_prdt_cd 추가
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display  = ("product", "save_trm", "intr_rate", "intr_rate2", "intr_rate_type_nm", "rsrv_type_nm") # "term_months" -> "save_trm", "rate" -> "intr_rate", 추가 정보 표시
    list_filter   = ("save_trm", "product", "intr_rate_type", "rsrv_type") # "term_months" -> "save_trm", 추가 필터
    search_fields = ("product__name", "product__fin_prdt_cd")


@admin.register(JoinedProduct)
class JoinedProductAdmin(admin.ModelAdmin):
    list_display  = ("user", "product", "option_display", "amount", "joined_at") # option 필드명 변경 제안
    list_filter   = ("product__name", "joined_at") # product 이름으로 필터링
    search_fields = ("user__username", "product__name")
    readonly_fields = ("joined_at",)

    @admin.display(description='가입 옵션 (기간, 이율)') # Admin 화면에 표시될 이름
    def option_display(self, obj):
        if obj.option:
            return f"{obj.option.save_trm}개월, {obj.option.intr_rate}% ({obj.option.intr_rate_type_nm})"
        return "-"