from celery import shared_task
from django.utils import timezone
import logging
import datetime # 추가
import re # 추가

from crawlers.services.toss import fetch_toss_comments 
# 변경: get_sentiment_openai -> classify_comments
from analysis.openai_sentiment import classify_comments 
from .models import InterestStock, Comment, StockAnalysis 

logger = logging.getLogger(__name__)

@shared_task
def crawl_and_analyze_stock_sentiments(interest_stock_id: int, stock_code: str, stock_name: str):
    logger.info(f"Starting sentiment analysis task for {stock_name} ({stock_code}), ID: {interest_stock_id}")
    
    try:
        interest_stock_obj = InterestStock.objects.get(id=interest_stock_id)
    except InterestStock.DoesNotExist:
        logger.error(f"InterestStock with ID {interest_stock_id} not found.")
        try:
            analysis_obj, created = StockAnalysis.objects.get_or_create(stock_id=interest_stock_id) # 이 부분은 stock_id가 InterestStock의 pk와 같다고 가정
            analysis_obj.task_status = StockAnalysis.FAILED
            analysis_obj.summary = f"관심 종목(ID: {interest_stock_id})을 찾을 수 없습니다."
            analysis_obj.batch_ready = False
            analysis_obj.save()
        except Exception as e_sa:
            logger.error(f"Failed to update StockAnalysis for non-existent InterestStock {interest_stock_id}: {e_sa}")
        return f"Failed: InterestStock {interest_stock_id} not found."

    analysis_obj, created = StockAnalysis.objects.update_or_create(
        stock=interest_stock_obj,
        defaults={
            'task_status': StockAnalysis.RUNNING,
            'updated_at': timezone.now(),
            'batch_ready': False 
        }
    )

    try:
        _crawled_company_name, crawled_stock_code, comments_data_list = fetch_toss_comments(company_name=interest_stock_obj.company_name)

        if not comments_data_list:
            logger.info(f"No comments returned by crawler for {stock_name} ({stock_code}).")
            analysis_obj.summary = f"{stock_name} ({stock_code})에 대한 댓글을 크롤러에서 찾을 수 없었습니다."
            analysis_obj.task_status = StockAnalysis.DONE 
            analysis_obj.batch_ready = True 
            analysis_obj.sentiment_stats = {
                'positive': 0, 'negative': 0, 'neutral': 0, 'Error': 0, # Error 카운트 추가
                'total_comments_fetched': 0, 'total_analyzed_successfully': 0
            }
            analysis_obj.save()
            return f"No comments found for {stock_code} via crawler."
        
        logger.info(f"Fetched {len(comments_data_list)} comments for {stock_name} ({stock_code})")

        # 댓글 내용만 추출하여 classify_comments 함수에 전달
        comment_texts = [item.get('content') for item in comments_data_list if item.get('content')]
        
        if not comment_texts:
            logger.info(f"No valid comment texts to analyze for {stock_name} ({stock_code}).")
            analysis_obj.summary = f"{stock_name} ({stock_code}): 분석할 댓글 내용이 없습니다."
            analysis_obj.task_status = StockAnalysis.DONE
            analysis_obj.batch_ready = True
            analysis_obj.sentiment_stats = {'total_comments_fetched': len(comments_data_list), 'total_analyzed_successfully': 0, 'positive':0, 'negative':0, 'neutral':0, 'Error':0}
            analysis_obj.save()
            return f"No valid comment content for {stock_code}."

        # classify_comments 함수는 감정 문자열 목록을 반환 (예: ["Positive", "Negative", "Neutral"])
        analyzed_sentiments = classify_comments(comment_texts)

        # 카운트 초기화
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        error_count = 0 # openai_sentiment.py에서 에러 발생 시 어떻게 반환되는지 확인 필요 (예: "Error" 문자열)

        Comment.objects.filter(analysis=analysis_obj).delete() # 이전 댓글 삭제

        # comments_data_list 와 analyzed_sentiments의 길이가 같다고 가정 (comment_texts 생성 시 None/빈 문자열 제외했으므로, 실제로는 comment_texts와 길이가 같음)
        # 원본 comments_data_list와 매칭시키기 위해 주의 필요. comment_texts에 포함된 댓글만 대상으로 함.
        
        comments_to_create = []
        analyzed_idx = 0 # analyzed_sentiments 목록의 인덱스

        for original_comment_data in comments_data_list:
            content = original_comment_data.get('content')
            sentiment_to_save = "" # 기본값

            if content and analyzed_idx < len(analyzed_sentiments) : # 분석된 결과가 있는 댓글만 처리
                sentiment_str = analyzed_sentiments[analyzed_idx]
                sentiment_to_save = sentiment_str # "Positive", "Negative", "Neutral" 또는 에러 시 다른 값

                if sentiment_str == "Positive": # classify_comments가 대소문자 어떻게 반환하는지 확인 필요 (openai_sentiment.py에서는 대문자 시작)
                    positive_count += 1
                elif sentiment_str == "Negative":
                    negative_count += 1
                elif sentiment_str == "Neutral":
                    neutral_count += 1
                else: # "Error" 또는 기타 값
                    error_count +=1
                analyzed_idx += 1
            elif content: # 내용은 있으나 분석 결과 목록에 없는 경우 (예: classify_comments가 일부만 반환한 경우)
                logger.warning(f"Sentiment for comment '{content[:20]}...' not found in results. Skipping sentiment saving.")
                error_count +=1 # 분석 못한 것으로 간주
            
            # written_at 처리 (crawlers/services/toss.py에서 datetime 객체로 변환하는 것이 가장 좋음)
            written_at_data = original_comment_data.get('written_at')
            final_written_at = None
            if isinstance(written_at_data, datetime.datetime):
                final_written_at = written_at_data
            elif isinstance(written_at_data, str):
                # 이미 crawlers/services/toss.py 의 parse_relative_time 에서 처리된 datetime 객체를 기대.
                # 만약 여전히 문자열이라면, 여기서 파싱 로직을 두거나, 크롤러 수정 필요.
                # 여기서는 크롤러에서 datetime 객체를 반환한다고 가정하고, 파싱 실패 시 현재시간.
                try:
                    # 이 부분은 parse_relative_time이 이미 datetime 객체를 반환하므로,
                    # 실제로는 if isinstance(written_at_data, str) 블록이 거의 실행되지 않아야 함.
                    # 하지만 안전장치로 남겨둘 수 있음.
                    if "시간 전" in written_at_data:
                        hours = int(re.search(r'\d+', written_at_data).group())
                        final_written_at = timezone.now() - datetime.timedelta(hours=hours)
                    elif "분 전" in written_at_data:
                        minutes = int(re.search(r'\d+', written_at_data).group())
                        final_written_at = timezone.now() - datetime.timedelta(minutes=minutes)
                    else:
                       final_written_at = timezone.now() 
                except:
                    final_written_at = timezone.now()
            else:
                final_written_at = timezone.now()

            comments_to_create.append(Comment(
                analysis=analysis_obj,
                author=original_comment_data.get('author', '익명'), 
                content=content or "", # content가 None일 경우 빈 문자열로
                sentiment=sentiment_to_save,
                likes=int(original_comment_data.get('likes', 0)), 
                written_at=final_written_at
            ))
        
        if comments_to_create:
            Comment.objects.bulk_create(comments_to_create)
        
        total_analyzed_successfully = positive_count + negative_count + neutral_count
        
        analysis_obj.summary = f"{stock_name} ({stock_code}) 댓글 {len(comments_data_list)}개 중 {total_analyzed_successfully}개 감정분석 완료."
        analysis_obj.sentiment_stats = {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'Error': error_count, # 에러 카운트 추가
            'total_comments_fetched': len(comments_data_list),
            'total_analyzed_successfully': total_analyzed_successfully,
        }
        analysis_obj.task_status = StockAnalysis.DONE
        analysis_obj.batch_ready = True
        analysis_obj.updated_at = timezone.now()
        analysis_obj.save()

        logger.info(f"Sentiment analysis task completed for {stock_name} ({stock_code}).")
        return f"Analysis complete for {stock_code}. Fetched: {len(comments_data_list)}, Analyzed: {total_analyzed_successfully}, Errors: {error_count}"

    except Exception as e_task:
        logger.error(f"Major error in sentiment analysis task for {stock_code}: {e_task}", exc_info=True)
        if 'analysis_obj' in locals():
            analysis_obj.task_status = StockAnalysis.FAILED
            analysis_obj.summary = f"분석 작업 중 오류 발생: {str(e_task)[:200]}"
            analysis_obj.batch_ready = False
            analysis_obj.save()
        return f"Failed sentiment analysis for {stock_code} due to critical error: {e_task}"