# Back/strategies/admin.py
from django.contrib import admin
from .models import Strategy, StrategyRun, StrategyTrade

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_public', 'is_paid', 'price_point', 'created_at')
    search_fields = ('user__username', 'name')
    list_filter = ('is_public', 'is_paid', 'created_at')

@admin.register(StrategyRun)
class StrategyRunAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'started_at', 'ended_at', 'total_return')
    search_fields = ('strategy__name',)
    list_filter = ('started_at',)

@admin.register(StrategyTrade)
class StrategyTradeAdmin(admin.ModelAdmin):
    list_display = ('run', 'stock_code', 'trade_type', 'price', 'quantity', 'traded_at')
    search_fields = ('stock_code',)
    list_filter = ('trade_type', 'traded_at')
