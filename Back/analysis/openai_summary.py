# back/analysis/openai_summary.py
import os, re, json, time, functools, logging, openai
from collections import Counter

from analysis.openai_sentiment import (
    safe_json_extract,
    classify_comments,
    time_logger,
    get_openai_client,
)

# ──────────────────────────────
# 로깅
# ──────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────
# GPT 요약·키워드
# ──────────────────────────────
@time_logger
def summarize_and_extract_keywords(comments: list[str]) -> dict:
    if not comments:
        return {"summary": "", "keywords": []}

    joined = "\n".join(comments)[:12000]
    resp = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "댓글을 800자 이내로 요약하고 상위 5~10 키워드를 추출해 "
                        "{\"summary\": \"...\", \"keywords\": [...]} 형태 JSON만 반환해."},
            {"role": "user",
             "content": f"Comments:\n{joined}\nJSON만, 한국어로."},
        ],
        temperature=0.3,
        max_tokens=512,
    )
    raw = resp.choices[0].message.content

    keywords = safe_json_extract(raw, "keywords")
    try:
        summary = json.loads(re.sub(r"```(?:json)?|```", "", raw).strip()).get("summary", "")
    except Exception:
        summary = ""
    return {"summary": summary, "keywords": keywords}

# ──────────────────────────────
# 통합 분석
# ──────────────────────────────
@time_logger
def analyze_comments(comments: list[str], company_name: str) -> dict:
    sentiments      = classify_comments(comments)
    sentiment_stats = dict(Counter(sentiments))
    summ            = summarize_and_extract_keywords(comments)
    return {
        "summary":         summ["summary"],
        "keywords":        summ["keywords"],
        "sentiments":      sentiments,
        "sentiment_stats": sentiment_stats,
    }
