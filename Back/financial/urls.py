# Back/financial/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views  # 사용하지 않는다면 제거 가능 (예: views.home, views.dashboard 가 실제로 이 파일에 정의되어 있는지 확인)
from django.conf import settings
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # 더 이상 여기서 직접 사용하지 않음

urlpatterns = [
    # 기본 페이지 (만약 financial/views.py에 정의되어 있다면)
    path('', views.home, name='home'),
    path('dashboard-page/', views.dashboard, name='dashboard'),

    # 웹 기반 앱 (Django Template을 사용하는 URL들)
    path('accounts/', include('accounts.urls')), # 일반적인 회원 관련 웹 페이지 (템플릿 뷰)
    path('community/', include('community.urls')),
    path('insight/', include('insight.urls')),
    path('simulator/', include('simulator.urls')),
    path('products/', include('financial_products.urls')),
    path('strategies/', include('strategies.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('notifications/', include('notifications.urls')),
    path('dashboard/', include('dashboard.urls')), # API가 아닌 웹페이지용 dashboard

    path('admin/', admin.site.urls),

    # --- API v1 엔드포인트들 ---
    # 모든 API 엔드포인트는 /api/v1/ 하위로 그룹화합니다.
    path('api/v1/accounts/', include('accounts.api.urls')), # JWT 토큰 발급, 갱신 및 /me/ 포함
    path('api/v1/community/', include('community.api.urls')),
    path('api/v1/insight/', include('insight.api.urls')),
    path('api/v1/simulator/', include('simulator.api.urls')),
    path('api/v1/products/', include('financial_products.api.urls')),
    path('api/v1/strategies/', include('strategies.api.urls')),
    path('api/v1/marketplace/', include('marketplace.api.urls')),
    path('api/v1/notifications/', include('notifications.api.urls')),
    path('api/v1/dashboard/', include('dashboard.api.urls')),
    path('api/v1/commodities/', include('commodities.api.urls')),
    path('api/v1/', include('bank_locations.api.urls')), # bank_locations.api.urls 내부에 'bank-locations/' 패턴이 있어야 함

    # 아래 JWT Auth 경로는 accounts.api.urls 내부로 이전되어 /api/v1/accounts/login/ 등으로 접근하게 됩니다.
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # 중복 제거
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 중복 제거
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]