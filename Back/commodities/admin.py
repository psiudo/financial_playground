# back/commodities/admin.py
from django.contrib import admin
from .models import Commodity, PriceHistory


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display  = ("name", "symbol", "created_at", "updated_at")
    search_fields = ("name", "symbol")


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display   = ("commodity", "date", "price")
    list_filter    = ("commodity",)
    date_hierarchy = "date"
