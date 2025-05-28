# Back/bank_locations/models.py
from django.db import models

class BankLocation(models.Model):
    bank_name = models.CharField(max_length=100) # 은행 이름
    branch_name = models.CharField(max_length=100, null=True, blank=True) # 지점 이름
    latitude = models.FloatField() # 위도
    longitude = models.FloatField() # 경도
    address = models.CharField(max_length=255, null=True, blank=True) # 주소

    def __str__(self):
        return f"{self.bank_name} - {self.branch_name or '본점'}"

    class Meta:
        verbose_name = "은행 위치"
        verbose_name_plural = "은행 위치 목록"