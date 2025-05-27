# api/urls.py

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('stocks/', views.interest_stocks, name='interest_stocks'),            # 관심 종목 리스트
    path('stocks/<int:stock_id>/analysis/', views.stock_analysis, name='stock_analysis'),  # 분석 결과
    path('stocks/<int:stock_id>/comments/', views.stock_comments, name='stock_comments'),  # 댓글 리스트
]
