# Back/accounts/views/social.py
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login

def google_login(request):
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    scope = 'openid email profile'
    state = 'random_state'  # CSRF 대응은 추후 처리

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scope}&state={state}"
    )
    return redirect(auth_url)

def google_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('accounts:login')

    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    token_response = requests.post(token_url, data=data).json()
    access_token = token_response.get('access_token')
    if not access_token:
        return redirect('accounts:login')

    userinfo = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    email = userinfo.get('email')
    name = userinfo.get('name')
    User = get_user_model()
    user, _ = User.objects.get_or_create(username=email, defaults={'first_name': name})
    login(request, user)
    return redirect('/')

def kakao_login(request):
    client_id = settings.KAKAO_REST_API_KEY
    redirect_uri = settings.KAKAO_REDIRECT_URI
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize"
        f"?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    )

def kakao_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('accounts:login')

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": settings.KAKAO_REDIRECT_URI,
        "code": code,
    }
    token_response = requests.post(token_url, data=data).json()
    access_token = token_response.get('access_token')
    if not access_token:
        return redirect('accounts:login')

    userinfo = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    kakao_account = userinfo.get('kakao_account', {})
    email = kakao_account.get('email')
    nickname = kakao_account.get('profile', {}).get('nickname')

    if not email:
        return redirect('accounts:login')

    User = get_user_model()
    user, _ = User.objects.get_or_create(username=email, defaults={'first_name': nickname})
    login(request, user)
    return redirect('/')
