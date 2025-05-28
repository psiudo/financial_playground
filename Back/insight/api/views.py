from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
import logging

from insight.models import InterestStock, StockAnalysis, Comment # models.py 경로에 맞게
from .serializers import StockAnalysisSerializer, InterestStockSerializer # serializers.py 경로에 맞게
from crawlers.services.toss import fetch_toss_comments # 크롤러 함수
from analysis.openai_sentiment import classify_comments # 분석 함수
from analysis.openai_summary import summarize_and_extract_keywords # 요약 함수 (필요시 사용)
from insight.tasks import crawl_and_analyze_stock_sentiments # Celery 작업 (관심종목용)

logger = logging.getLogger(__name__)

def _process_and_analyze_comments(stock_name_or_code, is_code=False):
    """
    종목명 또는 코드를 받아 댓글을 크롤링하고 감정 분석을 수행하는 내부 함수.
    DB 저장은 하지 않고 분석 결과만 반환.
    """
    if is_code:
        # stock_code로 company_name을 알아내는 과정이 필요하나,
        # 현재 fetch_toss_comments는 company_name을 인자로 받으므로,
        # 사용자가 code와 name을 같이 입력하거나, code로 name을 찾는 로직이 크롤러에 필요.
        # 여기서는 임시로 code를 name처럼 사용 (크롤러가 이를 처리한다고 가정)
        # 또는, 별도의 API(예: 한국거래소 API)로 종목코드로 종목명을 가져와야 함.
        # 지금은 stock_code를 company_name으로 간주하고 크롤러에 전달합니다.
        # 실제로는 이 부분이 개선되어야 합니다.
        company_name_to_crawl = stock_name_or_code 
        logger.info(f"Analyzing by CODE (used as name for crawler): {stock_name_or_code}")
    else:
        company_name_to_crawl = stock_name_or_code
        logger.info(f"Analyzing by NAME: {stock_name_or_code}")

    try:
        # 크롤러 호출
        crawled_company_name, crawled_stock_code, comments_data_list = fetch_toss_comments(company_name=company_name_to_crawl)

        if not crawled_stock_code: # 크롤러가 종목 코드를 못 찾으면 에러
             return None, None, {'error': f"'{company_name_to_crawl}'에 해당하는 종목 정보를 토스에서 찾을 수 없습니다. 정확한 종목명으로 검색해주세요."}

        if not comments_data_list:
            logger.info(f"No comments found by crawler for {crawled_company_name} ({crawled_stock_code}).")
            # 분석 결과가 없음을 나타내는 기본 구조 반환
            return crawled_company_name, crawled_stock_code, {
                'stock': {'company_name': crawled_company_name, 'stock_code': crawled_stock_code},
                'summary': "댓글을 찾을 수 없었습니다.",
                'keywords': [],
                'sentiment_stats': {'positive': 0, 'negative': 0, 'neutral': 0, 'error': 0, 'total_comments_fetched': 0, 'total_analyzed_successfully': 0},
                'batch_ready': True, # 댓글이 없어도 분석은 "완료"된 것으로 간주
                'task_status': StockAnalysis.DONE, # models.py에 정의된 DONE 사용
                'updated_at': timezone.now().isoformat(),
                'overall_sentiment_display': "정보 없음"
            }

        comment_texts = [item.get('content') for item in comments_data_list if item.get('content')]
        if not comment_texts:
            logger.info(f"No valid comment texts to analyze for {crawled_company_name} ({crawled_stock_code}).")
            return crawled_company_name, crawled_stock_code, {
                'stock': {'company_name': crawled_company_name, 'stock_code': crawled_stock_code},
                'summary': "분석할 댓글 내용이 없습니다.",
                'keywords': [],
                'sentiment_stats': {'positive': 0, 'negative': 0, 'neutral': 0, 'error': 0, 'total_comments_fetched': len(comments_data_list), 'total_analyzed_successfully': 0},
                'batch_ready': True,
                'task_status': StockAnalysis.DONE,
                'updated_at': timezone.now().isoformat(),
                'overall_sentiment_display': "정보 없음"
            }
        
        analyzed_sentiments = classify_comments(comment_texts)
        
        sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0} # OpenAI 반환값 기준
        for sentiment_str in analyzed_sentiments:
            sentiment_counts[sentiment_str] = sentiment_counts.get(sentiment_str, 0) + 1
        
        total_analyzed_successfully = sum(sentiment_counts.values())

        # overall_sentiment 계산
        overall_sentiment_str = "중립적"
        if sentiment_counts['Positive'] > sentiment_counts['Negative'] and sentiment_counts['Positive'] > sentiment_counts['Neutral']:
            overall_sentiment_str = "긍정적"
        elif sentiment_counts['Negative'] > sentiment_counts['Positive'] and sentiment_counts['Negative'] > sentiment_counts['Neutral']:
            overall_sentiment_str = "부정적"
        elif sentiment_counts['Neutral'] >= sentiment_counts['Positive'] and sentiment_counts['Neutral'] >= sentiment_counts['Negative']:
             overall_sentiment_str = "중립적"
        else: # 애매한 경우
            overall_sentiment_str = "혼재됨"


        # 프론트엔드에서 사용할 형태로 결과 데이터 구성 (StockAnalysisSerializer 형태와 유사하게)
        analysis_result_data = {
            'stock': { # InterestStockSerializer 형태와 유사하게
                'company_name': crawled_company_name, # 크롤러가 반환한 정확한 회사명
                'stock_code': crawled_stock_code,   # 크롤러가 반환한 정확한 종목 코드
            },
            'summary': f"{crawled_company_name} 댓글 {len(comments_data_list)}개 중 {total_analyzed_successfully}개 감정분석 완료.",
            'keywords': [], # 키워드 추출은 summarize_and_extract_keywords 함수 사용 필요 (여기서는 생략)
            'sentiment_stats': { # 소문자 키로 통일
                'positive': sentiment_counts.get('Positive', 0),
                'negative': sentiment_counts.get('Negative', 0),
                'neutral': sentiment_counts.get('Neutral', 0),
                'error': len(comment_texts) - total_analyzed_successfully, # classify_comments가 에러 반환 안하면 이렇게 계산
                'total_comments_fetched': len(comments_data_list),
                'total_analyzed_successfully': total_analyzed_successfully,
            },
            'batch_ready': True,
            'task_status': StockAnalysis.DONE, # models.py에 정의된 DONE 사용
            'updated_at': timezone.now().isoformat(), # ISO 형식 문자열로 전달
            'overall_sentiment_display': overall_sentiment_str 
        }
        return crawled_company_name, crawled_stock_code, analysis_result_data

    except Exception as e:
        logger.error(f"Error in _process_and_analyze_comments for {stock_name_or_code}: {e}", exc_info=True)
        return None, None, {'error': f"'{stock_name_or_code}' 분석 중 오류가 발생했습니다: {str(e)}"}


@api_view(['GET'])
@permission_classes([AllowAny]) # 누구나 검색은 가능하도록
def analyze_stock_on_the_fly(request):
    """
    쿼리 파라미터로 'name' 또는 'code'를 받아 실시간으로 분석 후 결과 반환 (DB 저장 X)
    예: /api/insight/realtime-analysis/?name=삼성전자
    예: /api/insight/realtime-analysis/?code=005930
    """
    stock_name = request.query_params.get('name')
    stock_code_param = request.query_params.get('code')

    if not stock_name and not stock_code_param:
        return Response({'error': "종목명('name') 또는 종목 코드('code')를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    if stock_code_param:
        # 사용자가 코드를 입력한 경우, 해당 코드를 크롤러에 전달 (크롤러가 코드->회사명 변환 기능이 없다면, 회사명도 함께 받아야 함)
        # 현재 fetch_toss_comments는 company_name을 받으므로, stock_code_param을 company_name처럼 사용
        # 실제로는 이 부분을 개선하여 stock_code로 검색 가능하게 하거나, 외부 API로 종목명 조회 필요
        crawled_name, crawled_code, result = _process_and_analyze_comments(stock_code_param, is_code=True)
    else: # stock_name으로 검색
        crawled_name, crawled_code, result = _process_and_analyze_comments(stock_name, is_code=False)

    if result and result.get('error'):
        return Response(result, status=status.HTTP_404_NOT_FOUND if "찾을 수 없습니다" in result.get('error', "") else status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if not result: # _process_and_analyze_comments에서 None, None, error_dict 반환 시
        return Response({'error': "분석 중 알 수 없는 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def add_interest_stock_and_request_analysis(request):
    """
    사용자의 관심 종목으로 추가하고, 백그라운드 분석을 요청합니다.
    요청 본문: {"stock_code": "005930", "company_name": "삼성전자"}
    """
    stock_code = request.data.get('stock_code')
    company_name = request.data.get('company_name')

    if not stock_code or not company_name:
        return Response({'error': "'stock_code'와 'company_name'을 모두 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        interest_stock, created = InterestStock.objects.get_or_create(
            user=request.user,
            stock_code=stock_code,
            defaults={'company_name': company_name}
        )
        if not created and interest_stock.company_name != company_name: # 이미 있는데 회사명 다르면 업데이트
            interest_stock.company_name = company_name
            interest_stock.save()
        
        logger.info(f"Interest stock {'created' if created else 'found'}: {interest_stock.company_name} ({interest_stock.stock_code}) for user {request.user.username}")

        # Celery 작업 호출 (DB에 저장된 InterestStock 대상으로)
        crawl_and_analyze_stock_sentiments.delay(
            interest_stock_id=interest_stock.id,
            stock_code=interest_stock.stock_code, 
            stock_name=interest_stock.company_name
        )
        
        # StockAnalysis 상태 초기화 또는 업데이트
        StockAnalysis.objects.update_or_create(
            stock=interest_stock,
            defaults={
                'batch_ready': False, 
                'task_status': StockAnalysis.WAITING,
                'summary': '', 
                'keywords': [], 
                'sentiment_stats': {},
                'updated_at': timezone.now()
            }
        )
        return Response({
            'message': f"'{interest_stock.company_name}'이(가) 관심 종목에 추가되었으며, 백그라운드 분석이 요청되었습니다. 잠시 후 '저장된 분석 결과 보기'에서 확인해주세요.",
            'interest_stock': InterestStockSerializer(interest_stock).data
        }, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        logger.error(f"Error adding interest stock and requesting analysis (stock_code: {stock_code}): {str(e)}", exc_info=True)
        return Response({'error': f"관심 종목 추가 및 분석 요청 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # 로그인한 사용자의 관심종목에 대한 분석 결과만
def get_my_stock_sentiment_analysis(request, interest_stock_id):
    """
    현재 사용자의 특정 관심 종목(InterestStock의 pk)에 대한 저장된 감정 분석 결과를 반환합니다.
    """
    try:
        interest_stock = get_object_or_404(InterestStock, id=interest_stock_id, user=request.user)
        analysis = get_object_or_404(StockAnalysis, stock=interest_stock)
        
        if not analysis.batch_ready:
            return Response({
                'message': '아직 분석 데이터가 준비되지 않았습니다. 잠시 후 다시 시도해주세요.',
                'stock_name': interest_stock.company_name,
                'task_status': analysis.task_status
            }, status=status.HTTP_202_ACCEPTED)
            
        serializer = StockAnalysisSerializer(analysis)
        return Response(serializer.data)
    except InterestStock.DoesNotExist:
        return Response({'error': "해당 관심 종목을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    except StockAnalysis.DoesNotExist:
        return Response({
            'message': f"'{interest_stock.company_name}' 종목에 대한 분석 결과가 아직 없습니다. 백그라운드 분석이 완료될 때까지 기다리거나, 새로고침 해주세요.",
            'stock_name': interest_stock.company_name,
            'task_status': StockAnalysis.WAITING # 분석 객체가 없으면 대기중으로 간주
        }, status=status.HTTP_204_NO_CONTENT) # 204 또는 다른 상태 코드 (예: 404인데 메시지 포함)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_interest_stocks_with_analysis_status(request):
    """
    현재 로그인한 사용자의 모든 관심 종목과 각각의 분석 상태를 함께 반환합니다.
    """
    my_interest_stocks = InterestStock.objects.filter(user=request.user).order_by('-created_at')
    response_data = []
    for istock in my_interest_stocks:
        data = InterestStockSerializer(istock).data
        try:
            analysis = istock.stockanalysis # OneToOneField 역참조
            data['analysis_status'] = analysis.task_status
            data['batch_ready'] = analysis.batch_ready
            data['last_analyzed_at'] = analysis.updated_at
            data['overall_sentiment_display'] = StockAnalysisSerializer().get_overall_sentiment_display(analysis) # Serializer 메소드 활용
        except StockAnalysis.DoesNotExist:
            data['analysis_status'] = StockAnalysis.WAITING # 분석 객체 없으면 '대기'
            data['batch_ready'] = False
            data['last_analyzed_at'] = None
            data['overall_sentiment_display'] = "N/A"
        response_data.append(data)
    return Response(response_data)