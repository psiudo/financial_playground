# insight/admin.py
from django.contrib import admin
from .models import InterestStock, StockAnalysis, Comment

admin.site.register(InterestStock)
admin.site.register(StockAnalysis)
admin.site.register(Comment)
