# analysis/openai_sentiment.py
import os, re, json, time, functools, logging, openai
from collections import Counter
from typing import Optional

# ──────────────────────────────
# 로깅
# ──────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────
# 실행 시간 측정용 데코레이터
# ──────────────────────────────
def time_logger(fn):
    @functools.wraps(fn)
    def wrap(*args, **kwargs):
        s = time.perf_counter()
        r = fn(*args, **kwargs)
        e = time.perf_counter()
        logger.info("%s 전체 실행 시간: %.4f초", fn.__name__, e - s)
        return r
    return wrap

# ──────────────────────────────
# OpenAI 클라이언트(지연 생성)
# ──────────────────────────────
def get_openai_client():
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ──────────────────────────────
# 안전 JSON 파서
# ──────────────────────────────
def safe_json_extract(txt: str, key: str, length: Optional[int] = None):
    try:
        txt  = re.sub(r"```(?:json)?|```", "", txt, flags=re.I).strip()
        data = json.loads(txt)
        val  = data.get(key, [])
        if isinstance(val, list):
            if length is not None and len(val) != length:
                raise ValueError("length mismatch")
            return val
    except Exception as e:
        logger.warning("safe_json_extract 실패: %s", e)
    return ["Neutral"] * length if length else []

# ──────────────────────────────
# 규칙 기반 감정 분류
# ──────────────────────────────
POS_HINT = {"😍", "👍", "good", "수익", "떡상", "🚀", "gain"}
NEG_HINT = {"ㅠ", "ㅜ", "bad", "하락", "폭락", "-10%", "loss"}

def rule_sentiment(text: str) -> Optional[str]:
    low = text.lower()
    if any(w in low for w in POS_HINT):
        return "Positive"
    if any(w in low for w in NEG_HINT):
        return "Negative"
    return None

# ──────────────────────────────
# GPT 감정 분류
# ──────────────────────────────
@time_logger
def _gpt_classify(texts: list[str]) -> list[str]:
    if not texts:
        return []
    joined = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    resp = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "각 문장을 Positive, Negative, Neutral 중 하나로만 분류해 "
                        "JSON {\"sentiments\": [...]} 형식으로만 응답해."},
            {"role": "user",
             "content": f"Comments:\n{joined}\nJSON 만, 한국어 라벨 그대로."},
        ],
        temperature=0,
        max_tokens=256,
    )
    raw = resp.choices[0].message.content
    return safe_json_extract(raw, "sentiments", length=len(texts))

# ──────────────────────────────
# 최종 감정 분류
# ──────────────────────────────
@time_logger
def classify_comments(comments: list[str]) -> list[str]:
    if not comments:
        return []
    rule = [rule_sentiment(c) for c in comments]
    need = [i for i, r in enumerate(rule) if r is None]
    if need:
        gpt_res = _gpt_classify([comments[i] for i in need])
        for i, s in zip(need, gpt_res):
            rule[i] = s
    return rule
