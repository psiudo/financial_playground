# Back/accounts/urls.py
from django.urls import path
from .views.user import signup_view, login_view, logout_view
from .views.auth import LoginAPI, LoginTokenAPI # 사용자 정의 API 로그인 뷰
from .views.social import google_login, google_callback, kakao_login, kakao_callback

app_name = 'accounts'

urlpatterns = [
    # 템플릿 기반 회원 관리 뷰
    path('signup/', signup_view, name='signup'),          # 최종 경로: /accounts/signup/
    path('login/', login_view, name='login'),            # 최종 경로: /accounts/login/
    path('logout/', logout_view, name='logout'),          # 최종 경로: /accounts/logout/

    # 사용자 정의 API 로그인 (Simple JWT와는 별개)
    # 최종 경로: /accounts/api/login/
    path('api/login/', LoginAPI.as_view(), name='custom_api_login'),
    # 최종 경로: /accounts/api/login-token/
    path('api/login-token/', LoginTokenAPI.as_view(), name='custom_login_token'),

    # 소셜 로그인 콜백 등
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/callback/', kakao_callback, name='kakao_callback'),
]