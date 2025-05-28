# Back/financial/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views # 이 import가 사용되지 않는다면 제거해도 됩니다.
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings

urlpatterns = [
    # 기본 페이지
    path('', views.home, name='home'), # 이 views.home이 정의되어 있어야 합니다.
    path('dashboard-page/', views.dashboard, name='dashboard'),  # html 페이지용 대시보드

    # 웹 기반 앱 (Django Template을 사용하는 URL들)
    path('accounts/',        include('accounts.urls')),
    path('community/',       include('community.urls')),
    path('insight/',         include('insight.urls')),
    path('simulator/',       include('simulator.urls')),
    path('products/',        include('financial_products.urls')),
    path('strategies/',      include('strategies.urls')),
    path('marketplace/',     include('marketplace.urls')),
    path('notifications/',   include('notifications.urls')),
    path('dashboard/',       include('dashboard.urls')), # API가 아닌 웹페이지용 dashboard일 경우
    path('admin/',           admin.site.urls),
    
    # API v1 엔드포인트들
    # path('api/v1/', include('api.urls')), # 만약 Back/api/urls.py가 있다면 이렇게 통합 가능
    
    # 앱별 API를 /api/v1/ 하위로 그룹화합니다.
    path('api/v1/accounts/', include('accounts.api.urls')),
    path('api/v1/community/', include('community.api.urls')), # community.api.urls가 존재해야 함
    path('api/v1/insight/', include('insight.api.urls')),
    path('api/v1/simulator/', include('simulator.api.urls')),
    path('api/v1/products/', include('financial_products.api.urls')),
    path('api/v1/strategies/', include('strategies.api.urls')),
    path('api/v1/marketplace/', include('marketplace.api.urls')),
    path('api/v1/notifications/', include('notifications.api.urls')),
    path('api/v1/dashboard/', include('dashboard.api.urls')), # API용 dashboard
    path('api/v1/commodities/', include('commodities.api.urls')),
    
    # ★★★ 은행 위치 API URL 포함 (프론트엔드 요청 경로에 맞춤) ★★★
    path('api/v1/', include('bank_locations.api.urls')), 
    # 위 라인에 의해 bank_locations.api.urls.py 내부의 'bank-locations/' 패턴이
    # 최종적으로 /api/v1/bank-locations/ 로 매칭됩니다.

    # 기존에 있던 path('api/bank_locations/', include('bank_locations.api.urls')), 라인은 삭제하거나 주석 처리합니다.
    # 이 라인이 있으면 /api/bank_locations/bank-locations/ 가 되어 프론트엔드 요청과 달라집니다.

    # JWT Auth
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
]

# Debug Toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]