from django.urls import path
from . import views

app_name = 'insight_api' # financial/urls.py 에서 include 시 namespace로 사용 가능

urlpatterns = [
    # 실시간 분석 API (DB 저장 없이 바로 결과 반환)
    path('realtime-analysis/', views.analyze_stock_on_the_fly, name='analyze_stock_on_the_fly'),

    # 사용자의 관심 종목 추가 및 백그라운드 분석 요청 API
    path('interest-stock/add-and-analyze/', views.add_interest_stock_and_request_analysis, name='add_interest_stock_and_request_analysis'),
    
    # 사용자의 관심 종목 목록 및 분석 상태 조회 API
    path('my-interest-stocks/', views.list_my_interest_stocks_with_analysis_status, name='list_my_interest_stocks_with_analysis_status'),

    # 사용자의 특정 관심 종목에 대한 저장된 분석 결과 조회 API (pk 기반)
    path('my-interest-stock/<int:interest_stock_id>/sentiment/', views.get_my_stock_sentiment_analysis, name='get_my_stock_sentiment_analysis'),

    # 기존 request_stock_sentiment_analysis API는 이제 add_interest_stock_and_request_analysis로 통합되거나,
    # 특정 관심 종목(DB에 이미 있는)에 대한 재분석 요청 용도로 변경될 수 있습니다.
    # path('stock/<str:stock_code>/request-analysis/', views.request_stock_sentiment_analysis, name='request_stock_sentiment_analysis'), # 필요시 유지 또는 수정

    # 참고: list_analyzed_stocks API는 현재 list_my_interest_stocks_with_analysis_status로 대체되거나,
    # "모든 사용자의 분석된 종목 중 인기 종목" 등을 보여주는 다른 용도로 사용될 수 있습니다.
    # path('stocks/analyzed/', views.list_analyzed_stocks, name='list_analyzed_stocks'), # 필요시 유지
]