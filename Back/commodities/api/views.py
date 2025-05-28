# Back/commodities/api/views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

# BankLocation 모델은 bank_locations 앱에서 가져옵니다.
from bank_locations.models import BankLocation

# BankLocationSerializer는 bank_locations 앱의 api/serializers.py 에서 가져옵니다.
# (만약 bank_locations/api/serializers.py에 BankLocationSerializer가 정의되어 있다면)
from bank_locations.api.serializers import BankLocationSerializer

# commodities 앱의 다른 View 및 Serializer import (예시)
from ..models import Commodity, PriceHistory # commodities.models에서 Commodity, PriceHistory 가져오기
from .serializers import CommodityListSerializer, PriceHistorySerializer # commodities.api.serializers에서 해당 serializer 가져오기


# Commodity 관련 API View들
class CommodityListAPIView(ListAPIView):
    queryset = Commodity.objects.all()
    serializer_class = CommodityListSerializer
    permission_classes = [AllowAny] # 필요에 따라 권한 설정

class CommodityHistoryAPIView(ListAPIView):
    # queryset = PriceHistory.objects.all() # 실제로는 필터링 필요
    serializer_class = PriceHistorySerializer
    permission_classes = [AllowAny] # 필요에 따라 권한 설정

    def get_queryset(self):
        symbol = self.kwargs.get('symbol')
        return PriceHistory.objects.filter(commodity__symbol=symbol)

# BankLocationListView (만약 이 위치에 계속 두어야 한다면)
class BankLocationListView(ListAPIView):
    queryset = BankLocation.objects.all()
    serializer_class = BankLocationSerializer # 위에서 수정한 import 경로로 가져옵니다.
    permission_classes = [AllowAny]