# financial/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings

urlpatterns = [
    # 기본 페이지
    path('', views.home, name='home'),
    path('dashboard-page/', views.dashboard, name='dashboard'),  # html 페이지용 대시보드

    # 웹 기반 앱
    path('accounts/',        include('accounts.urls')),
    path('community/',       include('community.urls')),
    path('insight/',         include('insight.urls')),
    path('simulator/',       include('simulator.urls')),
    path('products/',        include('financial_products.urls')),
    path('strategies/',      include('strategies.urls')),
    path('marketplace/',     include('marketplace.urls')),
    path('notifications/',   include('notifications.urls')),
    path('dashboard/',       include('dashboard.urls')),
    path('admin/',           admin.site.urls),

    # API endpoint: 앱별 API urls 분리
    path("api/community/", include("community.api.urls")),
    path('api/accounts/',      include('accounts.api.urls')),
    path('api/insight/', include('insight.api.urls')),
    path('api/simulator/', include('simulator.api.urls')),
    path('api/products/', include('financial_products.api.urls')),
    path('api/strategies/', include('strategies.api.urls')),
    path('api/marketplace/', include('marketplace.api.urls')),
    path('api/notifications/', include('notifications.api.urls')),
    path('api/dashboard/', include('dashboard.api.urls')),
    path('api/bank_locations/', include('bank_locations.api.urls')),
    path('api/commodities/', include('commodities.api.urls')),


    # JWT Auth
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
]

# Debug Toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
