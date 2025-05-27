# Back/simulator/admin.py
from django.contrib import admin
from .models import VirtualPortfolio, VirtualTrade

admin.site.register(VirtualPortfolio)
admin.site.register(VirtualTrade)
