# insight/tasks.py
"""
Celery 비동기 작업 정의
• fetch_and_save_comments  → 댓글 크롤링 및 DB 저장
• analyze_stock_comments   → 댓글 감정 분석(OpenAI)
• summarize_analysis       → 요약·키워드·통계 생성
실패 시 task_status = failed 로 저장
"""

import logging
from celery import shared_task
from insight.models import StockAnalysis
from analysis.services import (
    fetch_and_save_comments,
    analyze_stock_comments,
    summarize_analysis,
)

logger = logging.getLogger(__name__)


@shared_task
def run_analysis_task(analysis_id):
    try:
        analysis = StockAnalysis.objects.get(pk=analysis_id)
        stock = analysis.stock

        # 1 단계: 댓글 수집
        fetch_and_save_comments(stock)

        # 2 단계: 감정 분석(OpenAI)
        analyze_stock_comments(analysis)

        # 3 단계: 요약 및 키워드
        summarize_analysis(analysis)

        analysis.task_status = StockAnalysis.DONE
        analysis.save(update_fields=["task_status"])
        logger.info("Analysis %s completed", analysis_id)

    except Exception as e:
        logger.exception("Analysis %s failed: %s", analysis_id, e)
        try:
            analysis.task_status = StockAnalysis.FAILED
            analysis.save(update_fields=["task_status"])
        except Exception:
            pass
        raise
