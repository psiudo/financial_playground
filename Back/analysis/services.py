# Back/analysis/services.py
import threading
from collections import Counter
from datetime import timedelta
from django.utils import timezone

from crawlers.services.toss import fetch_toss_comments
from insight.models import Comment, StockAnalysis
from analysis.openai_sentiment import classify_comments
from analysis.openai_summary import summarize_and_extract_keywords

# ─────────────────────────────────────────────
# 내부 헬퍼: “3일 전”, “2시간 전”, “15분 전” 같은 문자열을 datetime 으로 변환
# ─────────────────────────────────────────────
def _parse_written_at(text: str):
    """
    상대 시각 문자열 → timezone-aware datetime
    실패 시 현재 시각을 반환해 ValidationError 를 피한다.
    """
    now = timezone.now()
    try:
        if "일 전" in text:
            days = int(text.split("일")[0])
            return now - timedelta(days=days)
        if "시간 전" in text:
            hours = int(text.split("시간")[0])
            return now - timedelta(hours=hours)
        if "분 전" in text:
            minutes = int(text.split("분")[0])
            return now - timedelta(minutes=minutes)
    except (ValueError, IndexError):
        pass
    return now

# ─────────────────────────────────────────────
def fetch_and_save_comments(stock):
    """
    1단계. Toss 댓글을 수집해 Comment 테이블에 저장
    """
    company_name_found, stock_code, comments = fetch_toss_comments(stock.company_name)

    if not comments:
        return None

    analysis, _ = StockAnalysis.objects.get_or_create(stock=stock)

    # 기존 댓글 초기화
    Comment.objects.filter(analysis=analysis).delete()

    # 새 댓글 저장
    Comment.objects.bulk_create([
        Comment(
            analysis=analysis,
            author=c["author"],
            content=c["content"],
            likes=c["likes"],
            written_at=_parse_written_at(c["written_at"]),   # ← 변환 적용
            sentiment="",
        )
        for c in comments
    ])

    # 분석 상태 초기화
    analysis.summary = ""
    analysis.keywords = []
    analysis.batch_ready = False
    analysis.sentiment_stats = {}
    analysis.save(update_fields=["summary", "keywords", "batch_ready", "sentiment_stats"])

    return analysis

# ─────────────────────────────────────────────
def analyze_stock_comments(analysis):
    """
    2단계. 감정 분석(OpenAI) 후 Comment.sentiment 및 통계 저장
    """
    comments_qs = analysis.comments.all()
    texts = [c.content for c in comments_qs]
    if not texts:
        return

    sentiments = classify_comments(texts)

    for c, s in zip(comments_qs, sentiments):
        c.sentiment = s
    Comment.objects.bulk_update(comments_qs, ["sentiment"])

    analysis.sentiment_stats = dict(Counter(sentiments))
    analysis.batch_ready = True
    analysis.save(update_fields=["sentiment_stats", "batch_ready"])

# ─────────────────────────────────────────────
def summarize_analysis(analysis):
    """
    3단계. 댓글을 요약·키워드 추출(OpenAI) 후 저장
    """
    texts = [c.content for c in analysis.comments.all()]
    if not texts:
        return

    summ = summarize_and_extract_keywords(texts)
    analysis.summary = summ["summary"]
    analysis.keywords = summ["keywords"]
    analysis.save(update_fields=["summary", "keywords"])
