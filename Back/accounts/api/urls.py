# Back/accounts/api/urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserProfileView

urlpatterns = [
    # Simple JWT 토큰 발급 (POST 요청: username, password)
    # 최종 경로: /api/v1/accounts/login/
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Simple JWT 토큰 갱신 (POST 요청: refresh)
    # 최종 경로: /api/v1/accounts/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 현재 로그인된 사용자 프로필 정보 (GET, PUT, PATCH 요청)
    # 최종 경로: /api/v1/accounts/me/
    path('me/', UserProfileView.as_view(), name='user_profile_me'), # name을 좀 더 명확하게 변경 가능
]