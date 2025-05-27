# accounts/urls.py
from django.urls import path
from .views.user import signup_view, login_view, logout_view
from .views.auth import LoginAPI, LoginTokenAPI
from .views.social import google_login, google_callback, kakao_login, kakao_callback

app_name = 'accounts'

urlpatterns = [
    # 템플릿 로그인
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # API 로그인
    path('api/login/', LoginAPI.as_view(), name='api_login'),
    path('api/login-token/', LoginTokenAPI.as_view(), name='login_token'),

    # 소셜 로그인
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('kakao/callback/', kakao_callback, name='kakao_callback'),
]
