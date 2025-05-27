# Back/marketplace/admin.py
from django.contrib import admin
from .models import MarketListing, Purchase

@admin.register(MarketListing)
class MarketListingAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'seller', 'price_point', 'sales', 'created_at')
    search_fields = ('strategy__name', 'seller__username')
    list_filter = ('created_at',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'listing', 'purchased_at')
    search_fields = ('buyer__username', 'listing__strategy__name')
    list_filter = ('purchased_at',)
