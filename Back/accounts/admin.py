# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PointTransaction

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Admin 목록에 보여줄 필드
    list_display = ("username", "email", "risk_grade", "point_balance", "is_staff")

    # 필드 그룹 편집
    fieldsets = UserAdmin.fieldsets + (
        ("추가 정보", {
            "fields": (
                "birth_date",
                "job",
                "annual_income",
                "risk_grade",
                "preferred_bank",
                "profile_image",
                "bio",
                "point_balance",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("추가 정보", {
            "fields": (
                "birth_date",
                "job",
                "annual_income",
                "risk_grade",
            )
        }),
    )
@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "delta_point", "kind", "reason", "created_at")
    list_filter  = ("kind", "created_at")
