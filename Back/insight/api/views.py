from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
import logging
from django.shortcuts import get_object_or_404 # 추가

from insight.models import InterestStock, StockAnalysis, Comment
from .serializers import StockAnalysisSerializer, InterestStockSerializer
from crawlers.services.toss import fetch_toss_comments
from analysis.openai_sentiment import classify_comments
from analysis.openai_summary import summarize_and_extract_keywords # 요약 및 키워드 추출 함수
from insight.tasks import crawl_and_analyze_stock_sentiments

logger = logging.getLogger(__name__)

def _process_and_analyze_comments(stock_name_or_code, is_code=False):
    """
    종목명 또는 코드를 받아 댓글을 크롤링하고 감정 분석 및 요약, 키워드 추출을 수행.
    DB 저장은 하지 않고 분석 결과만 반환.
    """
    company_name_to_crawl = stock_name_or_code
    log_prefix = f"Analyzing by {'CODE' if is_code else 'NAME'}: {stock_name_or_code}"
    logger.info(log_prefix)

    try:
        crawled_company_name, crawled_stock_code, comments_data_list = fetch_toss_comments(company_name=company_name_to_crawl)

        if not crawled_stock_code:
            error_msg = f"'{company_name_to_crawl}'에 해당하는 종목 정보를 토스에서 찾을 수 없습니다. 정확한 종목명으로 검색해주세요."
            logger.warning(f"{log_prefix} - {error_msg}")
            return None, None, {'error': error_msg, 'stock_name_searched': company_name_to_crawl}

        if not comments_data_list:
            logger.info(f"No comments found by crawler for {crawled_company_name} ({crawled_stock_code}).")
            return crawled_company_name, crawled_stock_code, {
                'stock': {'company_name': crawled_company_name, 'stock_code': crawled_stock_code},
                'summary': "수집된 댓글이 없습니다.",
                'keywords': [],
                'sentiment_stats': {'positive': 0, 'negative': 0, 'neutral': 0, 'error': 0, 'total_comments_fetched': 0, 'total_analyzed_successfully': 0},
                'batch_ready': True,
                'task_status': StockAnalysis.DONE,
                'updated_at': timezone.now().isoformat(),
                'overall_sentiment_display': "정보 없음"
            }

        comment_texts = [item.get('content') for item in comments_data_list if item.get('content')]
        if not comment_texts:
            logger.info(f"No valid comment texts to analyze for {crawled_company_name} ({crawled_stock_code}).")
            return crawled_company_name, crawled_stock_code, {
                'stock': {'company_name': crawled_company_name, 'stock_code': crawled_stock_code},
                'summary': "분석할 유효한 댓글 내용이 없습니다.",
                'keywords': [],
                'sentiment_stats': {'positive': 0, 'negative': 0, 'neutral': 0, 'error': 0, 'total_comments_fetched': len(comments_data_list), 'total_analyzed_successfully': 0},
                'batch_ready': True,
                'task_status': StockAnalysis.DONE,
                'updated_at': timezone.now().isoformat(),
                'overall_sentiment_display': "정보 없음"
            }
        
        # 감정 분석
        analyzed_sentiments = classify_comments(comment_texts)
        
        sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        # classify_comments가 반환하는 레이블이 정확히 'Positive', 'Negative', 'Neutral'인지 확인 필요
        for sentiment_str in analyzed_sentiments:
            if sentiment_str in sentiment_counts:
                sentiment_counts[sentiment_str] += 1
            else: # 예상치 못한 레이블 처리 (예: 'Error' 등)
                sentiment_counts['Neutral'] +=1 # 기본적으로 중립으로 처리하거나, 에러 카운트 별도 관리
                logger.warning(f"Unexpected sentiment label '{sentiment_str}' received. Counted as Neutral.")

        total_analyzed_successfully = sum(sentiment_counts.values())

        # 요약 및 키워드 추출 (OpenAI API 호출)
        summary_info = {"summary": f"{crawled_company_name} 댓글 {len(comments_data_list)}개 중 {total_analyzed_successfully}개 감정분석 완료.", "keywords": []}
        if comment_texts: # 댓글 내용이 있을 때만 시도
            try:
                summary_info = summarize_and_extract_keywords(comment_texts)
                logger.info(f"Summary and keywords extracted for {crawled_company_name}")
            except Exception as e_sum:
                logger.error(f"Error during summarization/keyword extraction for {crawled_company_name}: {e_sum}", exc_info=True)
                # 요약/키워드 추출 실패 시, 기본 요약 메시지 사용

        # 종합 감정 판단
        overall_sentiment_str = "중립적"
        # OpenAI가 반환하는 레이블('Positive', 'Negative', 'Neutral')에 맞춰 키 사용
        pos_count = sentiment_counts.get('Positive', 0)
        neg_count = sentiment_counts.get('Negative', 0)
        neu_count = sentiment_counts.get('Neutral', 0)

        if pos_count > neg_count and pos_count >= neu_count: # 긍정이 가장 많거나 중립과 동률일때도 긍정 우위로
            overall_sentiment_str = "긍정적"
        elif neg_count > pos_count and neg_count >= neu_count: # 부정이 가장 많거나 중립과 동률일때도 부정 우위로
            overall_sentiment_str = "부정적"
        elif neu_count > pos_count and neu_count > neg_count: # 중립이 명확히 많을 때
             overall_sentiment_str = "중립적"
        elif pos_count == neg_count and pos_count > neu_count: # 긍정과 부정이 같고 중립보다 많으면 혼재
            overall_sentiment_str = "혼재됨"
        elif total_analyzed_successfully == 0 : # 분석된 댓글이 없을 경우
            overall_sentiment_str = "정보 없음"
        # 그 외 모든 경우는 중립적 또는 혼재됨으로 처리 (예: 긍정=중립 > 부정)
        
        analysis_result_data = {
            'stock': {
                'company_name': crawled_company_name,
                'stock_code': crawled_stock_code,
            },
            'summary': summary_info.get("summary"),
            'keywords': summary_info.get("keywords", []),
            'sentiment_stats': {
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count,
                'error': len(comment_texts) - total_analyzed_successfully, # GPT가 일부 분석 못했을 경우
                'total_comments_fetched': len(comments_data_list),
                'total_analyzed_successfully': total_analyzed_successfully,
            },
            'batch_ready': True,
            'task_status': StockAnalysis.DONE,
            'updated_at': timezone.now().isoformat(),
            'overall_sentiment_display': overall_sentiment_str
        }
        return crawled_company_name, crawled_stock_code, analysis_result_data

    except NotImplementedError as nie: # get_driver() 미구현 에러 처리
        logger.critical(f"WebDriver 로드 실패: {nie}")
        return None, None, {'error': f"크롤러 실행에 필요한 WebDriver 설정 오류입니다. {str(nie)}", 'stock_name_searched': stock_name_or_code}
    except Exception as e:
        logger.error(f"Error in _process_and_analyze_comments for {stock_name_or_code}: {e}", exc_info=True)
        return None, None, {'error': f"'{stock_name_or_code}' 분석 중 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", 'details': str(e), 'stock_name_searched': stock_name_or_code}


@api_view(['GET'])
@permission_classes([AllowAny])
def analyze_stock_on_the_fly(request):
    stock_name = request.query_params.get('name')
    stock_code_param = request.query_params.get('code')

    if not stock_name and not stock_code_param:
        return Response({'error': "종목명('name') 또는 종목 코드('code')를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    # 종목 코드 우선, 없으면 종목명 사용
    query_value = stock_code_param if stock_code_param else stock_name
    is_code_search = bool(stock_code_param)
    
    crawled_name, crawled_code, result = _process_and_analyze_comments(query_value, is_code=is_code_search)

    if result and result.get('error'):
        # 에러 메시지에 검색한 종목명/코드를 포함시켜 사용자에게 명확한 피드백 제공
        error_detail = result.get('error')
        searched_term = result.get('stock_name_searched', query_value) # _process_and_analyze_comments에서 전달받은 검색어 사용
        
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if "찾을 수 없습니다" in error_detail or "WebDriver" in error_detail : # 크롤러 또는 WebDriver 관련 주요 실패
            status_code = status.HTTP_404_NOT_FOUND # 또는 SERVICE_UNAVAILABLE
        
        return Response({'error': error_detail, 'searched_term': searched_term}, status=status_code)
    
    if not result:
        return Response({'error': f"'{query_value}' 분석 중 알 수 없는 오류가 발생했습니다.", 'searched_term': query_value}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def add_interest_stock_and_request_analysis(request):
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
        if not created and interest_stock.company_name != company_name:
            interest_stock.company_name = company_name
            interest_stock.save(update_fields=['company_name'])
        
        logger.info(f"Interest stock {'created' if created else 'found'}: {interest_stock.company_name} ({interest_stock.stock_code}) for user {request.user.username}")

        # StockAnalysis 상태를 '대기 중'으로 설정하고 Celery 작업 트리거
        analysis_obj, analysis_created = StockAnalysis.objects.update_or_create(
            stock=interest_stock,
            defaults={
                'task_status': StockAnalysis.WAITING, # 작업을 요청했으므로 WAITING으로 설정
                'batch_ready': False, # 아직 결과 준비 안됨
                'summary': '분석 대기 중입니다...' if analysis_created else (analysis_obj.summary or '분석 대기 중입니다...'),
                'keywords': [] if analysis_created else (analysis_obj.keywords or []),
                'sentiment_stats': {} if analysis_created else (analysis_obj.sentiment_stats or {}),
                'updated_at': timezone.now()
            }
        )
        
        crawl_and_analyze_stock_sentiments.delay(
            interest_stock_id=interest_stock.id,
            stock_code=interest_stock.stock_code, 
            stock_name=interest_stock.company_name
        )
        
        return Response({
            'message': f"'{interest_stock.company_name}' 관심 종목 {'추가 및' if created else ''} 백그라운드 분석이 요청되었습니다. 잠시 후 '저장된 분석 결과 보기'에서 확인해주세요.",
            'interest_stock': InterestStockSerializer(interest_stock).data,
            'analysis_status': analysis_obj.task_status
        }, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        logger.error(f"Error adding interest stock and requesting analysis (stock_code: {stock_code}): {str(e)}", exc_info=True)
        return Response({'error': f"관심 종목 추가 및 분석 요청 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_stock_sentiment_analysis(request, interest_stock_id):
    interest_stock = get_object_or_404(InterestStock, id=interest_stock_id, user=request.user)
    try:
        analysis = StockAnalysis.objects.get(stock=interest_stock)
        if not analysis.batch_ready and analysis.task_status not in [StockAnalysis.DONE, StockAnalysis.FAILED]:
            return Response({
                'message': f"'{interest_stock.company_name}' 종목에 대한 분석이 현재 '{analysis.get_task_status_display()}' 상태입니다. 잠시 후 다시 시도해주세요.",
                'stock_name': interest_stock.company_name,
                'stock_code': interest_stock.stock_code,
                'task_status': analysis.task_status,
                'batch_ready': analysis.batch_ready,
                'updated_at': analysis.updated_at.isoformat() if analysis.updated_at else None,
            }, status=status.HTTP_202_ACCEPTED)
        
        serializer = StockAnalysisSerializer(analysis)
        return Response(serializer.data)
    except StockAnalysis.DoesNotExist:
        # 분석 객체가 없으면, 백그라운드 분석 요청을 한 번 더 시도해볼 수 있도록 유도하거나,
        # WAITING 상태로 간주하고 메시지 반환
        StockAnalysis.objects.update_or_create(
            stock=interest_stock,
            defaults={'task_status': StockAnalysis.WAITING, 'batch_ready': False}
        ) # 없으면 WAITING으로 생성
        return Response({
            'message': f"'{interest_stock.company_name}' 종목에 대한 분석 결과가 아직 없습니다. 백그라운드 분석이 요청되었으니 잠시 후 새로고침 해주세요.",
            'stock_name': interest_stock.company_name,
            'stock_code': interest_stock.stock_code,
            'task_status': StockAnalysis.WAITING,
            'batch_ready': False,
            'updated_at': timezone.now().isoformat(),
        }, status=status.HTTP_202_ACCEPTED) # 202 Accepted 또는 204 No Content
    except Exception as e:
        logger.error(f"Error fetching saved analysis for {interest_stock_id}: {e}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_interest_stocks_with_analysis_status(request):
    my_interest_stocks = InterestStock.objects.filter(user=request.user).select_related('stockanalysis').order_by('-created_at')
    response_data = []
    for istock in my_interest_stocks:
        data = InterestStockSerializer(istock).data
        try:
            analysis = istock.stockanalysis # OneToOneField 역참조 (위에서 select_related로 이미 가져옴)
            data['analysis_id'] = analysis.id
            data['analysis_status'] = analysis.task_status
            data['analysis_status_display'] = analysis.get_task_status_display()
            data['batch_ready'] = analysis.batch_ready
            data['last_analyzed_at'] = analysis.updated_at.isoformat() if analysis.updated_at else None
            data['overall_sentiment_display'] = StockAnalysisSerializer().get_overall_sentiment_display(analysis)
        except StockAnalysis.DoesNotExist:
            data['analysis_id'] = None
            data['analysis_status'] = StockAnalysis.WAITING
            data['analysis_status_display'] = dict(StockAnalysis.STATUS_CHOICES).get(StockAnalysis.WAITING)
            data['batch_ready'] = False
            data['last_analyzed_at'] = None
            data['overall_sentiment_display'] = "N/A"
        response_data.append(data)
    return Response(response_data)