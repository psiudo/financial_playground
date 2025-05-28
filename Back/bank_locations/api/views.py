# Back/bank_locations/api/views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny # ★ AllowAny를 import 합니다.
from ..models import BankLocation
from .serializers import BankLocationSerializer

class BankLocationListView(ListAPIView):
    queryset = BankLocation.objects.all()
    serializer_class = BankLocationSerializer
    permission_classes = [AllowAny] # ★★★ 모든 사용자의 접근을 허용합니다. ★★★
    # pagination_class = None # 페이지네이션 없이 모든 결과를 반환하려면 주석 해제