# Back/bank_locations/api/serializers.py
from rest_framework import serializers
# models.py 경로는 실제 프로젝트 구조에 따라 다를 수 있으므로, 
# 현재 bank_locations 앱 내에 models.py가 있다면 아래와 같이 수정합니다.
from ..models import BankLocation 

class BankLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankLocation
        # 프론트엔드에서 필요한 필드들을 여기에 나열합니다.
        fields = ['id', 'bank_name', 'branch_name', 'latitude', 'longitude', 'address']