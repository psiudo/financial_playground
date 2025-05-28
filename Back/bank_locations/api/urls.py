# Back/bank_locations/api/urls.py
from django.urls import path
from . import views # 같은 디렉토리의 views.py를 가져옵니다.

app_name = 'bank_locations_api' # URL 패턴의 네임스페이스 (선택 사항)

urlpatterns = [
    # GET /api/v1/bank-locations/ 또는 /api/bank_locations/bank-locations/ (아래 5번 항목 참고)
    # 요청 시 BankLocationListView가 실행됩니다.
    path('bank-locations/', views.BankLocationListView.as_view(), name='banklocation-list'),
]