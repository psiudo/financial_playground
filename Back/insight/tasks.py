from celery import shared_task
from django.utils import timezone
import logging
import datetime
import re

from crawlers.services.toss import fetch_toss_comments
from analysis.openai_sentiment import classify_comments
from analysis.openai_summary import summarize_and_extract_keywords # 요약 및 키워드 추출 함수 추가
from .models import InterestStock, Comment, StockAnalysis

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60 * 5) # bind=True for self, 재시도 설정 추가
def crawl_and_analyze_stock_sentiments(self, interest_stock_id: int, stock_code: str, stock_name: str):
    task_log_prefix = f"[CeleryTask ID: {self.request.id if self.request else 'Unknown'}] Stock: {stock_name}({stock_code})"
    logger.info(f"{task_log_prefix} - Sentiment analysis task STARTING for InterestStock ID: {interest_stock_id}")

    try:
        interest_stock_obj = InterestStock.objects.get(id=interest_stock_id)
    except InterestStock.DoesNotExist:
        logger.error(f"{task_log_prefix} - InterestStock with ID {interest_stock_id} not found. Task cannot proceed.")
        # StockAnalysis 상태를 FAILED로 업데이트 시도 (stock_id가 InterestStock의 pk를 사용한다고 가정)
        StockAnalysis.objects.filter(stock_id=interest_stock_id).update(
            task_status=StockAnalysis.FAILED,
            summary=f"관심 종목(ID: {interest_stock_id})을 찾을 수 없어 분석을 진행할 수 없습니다.",
            batch_ready=False,
            updated_at=timezone.now()
        )
        return f"Failed: InterestStock {interest_stock_id} not found."

    # StockAnalysis 객체를 가져오거나 생성하고, 상태를 RUNNING으로 업데이트
    analysis_obj, created = StockAnalysis.objects.update_or_create(
        stock=interest_stock_obj,
        defaults={
            'task_status': StockAnalysis.RUNNING,
            'updated_at': timezone.now(),
            'batch_ready': False # 분석 시작 시 항상 False로 초기화
        }
    )
    if created:
        logger.info(f"{task_log_prefix} - New StockAnalysis record created.")
    else:
        logger.info(f"{task_log_prefix} - Existing StockAnalysis record updated to RUNNING.")

    try:
        # 1. 댓글 크롤링
        # fetch_toss_comments는 (크롤링된 회사명, 크롤링된 종목코드, 댓글리스트) 반환
        _crawled_company_name, crawled_stock_code, comments_data_list = fetch_toss_comments(
            company_name=interest_stock_obj.company_name, 
            max_comments=200 # 최대 댓글 수 제한 (Celery 작업에서는 더 많이 가져와도 괜찮음)
        )
        
        # 크롤러가 회사명이나 종목코드를 다르게 찾았을 경우, interest_stock_obj 업데이트 (선택적)
        if _crawled_company_name and interest_stock_obj.company_name != _crawled_company_name:
            logger.info(f"{task_log_prefix} - Company name updated by crawler: {interest_stock_obj.company_name} -> {_crawled_company_name}")
            interest_stock_obj.company_name = _crawled_company_name
        if crawled_stock_code and interest_stock_obj.stock_code != crawled_stock_code:
            logger.info(f"{task_log_prefix} - Stock code updated by crawler: {interest_stock_obj.stock_code} -> {crawled_stock_code}")
            interest_stock_obj.stock_code = crawled_stock_code
        if interest_stock_obj.is_dirty(check_fields=True): # 변경사항이 있을 경우에만 저장
            interest_stock_obj.save()


        if not comments_data_list:
            logger.info(f"{task_log_prefix} - No comments returned by crawler.")
            analysis_obj.summary = f"{interest_stock_obj.company_name} ({interest_stock_obj.stock_code})에 대한 댓글을 찾을 수 없었습니다."
            analysis_obj.task_status = StockAnalysis.DONE
            analysis_obj.batch_ready = True
            analysis_obj.sentiment_stats = {'positive': 0, 'negative': 0, 'neutral': 0, 'error': 0, 'total_comments_fetched': 0, 'total_analyzed_successfully': 0}
            analysis_obj.keywords = []
            analysis_obj.save()
            return f"{task_log_prefix} - No comments found via crawler."
        
        logger.info(f"{task_log_prefix} - Fetched {len(comments_data_list)} comments.")

        comment_texts = [item.get('content') for item in comments_data_list if item.get('content')]
        if not comment_texts:
            logger.info(f"{task_log_prefix} - No valid comment texts to analyze.")
            analysis_obj.summary = f"{interest_stock_obj.company_name} ({interest_stock_obj.stock_code}): 분석할 댓글 내용이 없습니다."
            analysis_obj.task_status = StockAnalysis.DONE
            analysis_obj.batch_ready = True
            analysis_obj.sentiment_stats = {'total_comments_fetched': len(comments_data_list), 'total_analyzed_successfully': 0, 'positive':0, 'negative':0, 'neutral':0, 'error':0}
            analysis_obj.keywords = []
            analysis_obj.save()
            return f"{task_log_prefix} - No valid comment content."

        # 2. 댓글 감정 분석 (OpenAI)
        logger.info(f"{task_log_prefix} - Starting sentiment classification for {len(comment_texts)} texts.")
        analyzed_sentiments = classify_comments(comment_texts)
        logger.info(f"{task_log_prefix} - Sentiment classification completed.")

        positive_count, negative_count, neutral_count, error_count = 0, 0, 0, 0
        for sentiment_str in analyzed_sentiments:
            if sentiment_str == "Positive":
                positive_count += 1
            elif sentiment_str == "Negative":
                negative_count += 1
            elif sentiment_str == "Neutral":
                neutral_count += 1
            else:
                error_count += 1
                logger.warning(f"{task_log_prefix} - Unexpected sentiment label '{sentiment_str}' encountered.")
        
        total_analyzed_successfully = positive_count + negative_count + neutral_count

        # 3. 댓글 요약 및 키워드 추출 (OpenAI) - 감정 분석 후 진행
        logger.info(f"{task_log_prefix} - Starting summary and keyword extraction.")
        summary_info = {"summary": "", "keywords": []}
        try:
            summary_info = summarize_and_extract_keywords(comment_texts)
            logger.info(f"{task_log_prefix} - Summary and keyword extraction completed.")
        except Exception as e_sum_task:
            logger.error(f"{task_log_prefix} - Error during summary/keyword extraction: {e_sum_task}", exc_info=True)
            analysis_obj.summary = f"{interest_stock_obj.company_name} ({interest_stock_obj.stock_code}) 댓글 {len(comments_data_list)}개 중 {total_analyzed_successfully}개 감정분석 완료. (요약 중 오류)"
        else:
            analysis_obj.summary = summary_info.get("summary", analysis_obj.summary) # 성공 시 GPT 요약으로 업데이트

        analysis_obj.keywords = summary_info.get("keywords", [])


        # 4. 분석된 댓글 및 통계 DB 저장
        Comment.objects.filter(analysis=analysis_obj).delete() # 기존 댓글 삭제

        comments_to_create = []
        analyzed_idx = 0
        for original_comment_data in comments_data_list:
            content = original_comment_data.get('content')
            sentiment_to_save = ""

            if content and analyzed_idx < len(analyzed_sentiments):
                sentiment_to_save = analyzed_sentiments[analyzed_idx]
                analyzed_idx += 1
            elif content: # 분석 결과 부족
                logger.warning(f"{task_log_prefix} - Sentiment for comment (idx: {analyzed_idx}) not found. Saving with no sentiment.")
                error_count +=1 # 분석 못한 것으로 간주

            written_at_dt = original_comment_data.get('written_at')
            # crawlers/services/toss.py의 parse_relative_time이 timezone-aware datetime 객체를 반환해야 함
            if not isinstance(written_at_dt, datetime.datetime):
                logger.warning(f"{task_log_prefix} - Invalid written_at data type: {type(written_at_dt)}. Using current time.")
                written_at_dt = timezone.now()
            elif timezone.is_naive(written_at_dt): # 혹시 naive datetime이면 aware로 변환
                 written_at_dt = timezone.make_aware(written_at_dt, timezone.get_current_timezone())


            comments_to_create.append(Comment(
                analysis=analysis_obj,
                author=original_comment_data.get('author', '익명'),
                content=content or "",
                sentiment=sentiment_to_save,
                likes=int(original_comment_data.get('likes', 0)),
                written_at=written_at_dt
            ))
        
        if comments_to_create:
            Comment.objects.bulk_create(comments_to_create)
            logger.info(f"{task_log_prefix} - {len(comments_to_create)} comments saved to DB.")
        
        analysis_obj.sentiment_stats = {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'error': error_count, # OpenAI 분석 실패 또는 예상 못한 레이블
            'total_comments_fetched': len(comments_data_list),
            'total_analyzed_successfully': total_analyzed_successfully,
        }
        analysis_obj.task_status = StockAnalysis.DONE
        analysis_obj.batch_ready = True
        analysis_obj.updated_at = timezone.now()
        analysis_obj.save()

        logger.info(f"{task_log_prefix} - Sentiment analysis task COMPLETED successfully.")
        return f"{task_log_prefix} - Analysis complete. Fetched: {len(comments_data_list)}, Analyzed: {total_analyzed_successfully}, Errors: {error_count}"

    except Exception as e_task_main:
        logger.error(f"{task_log_prefix} - CRITICAL error in sentiment analysis task: {e_task_main}", exc_info=True)
        if 'analysis_obj' in locals() and analysis_obj: # analysis_obj가 정의되어 있다면
            analysis_obj.task_status = StockAnalysis.FAILED
            analysis_obj.summary = f"분석 작업 중 심각한 오류 발생: {str(e_task_main)[:200]}" # 에러 메시지 일부 저장
            analysis_obj.batch_ready = False # 분석 실패 시 False
            analysis_obj.save()
        
        # Celery 작업 재시도 로직 (선택적, 특정 예외에 대해서만 재시도)
        # if isinstance(e_task_main, (ConnectionError, TimeoutError)): # 예시: 네트워크 관련 에러 시 재시도
        #     raise self.retry(exc=e_task_main)
        return f"{task_log_prefix} - Failed due to critical error: {e_task_main}"