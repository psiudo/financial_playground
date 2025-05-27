# crawlers/services/toss.py
import os, re, time, logging, functools, datetime
from selenium.webdriver.common.by    import By
from selenium.webdriver.common.keys  import Keys
from selenium.webdriver.support.ui   import WebDriverWait
from selenium.webdriver.support      import expected_conditions as EC
from selenium.common.exceptions      import StaleElementReferenceException

from utils.driver_pool import get_driver

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def time_logger(fn):
    @functools.wraps(fn)
    def wrap(*a, **kw):
        s = time.perf_counter()
        r = fn(*a, **kw)
        e = time.perf_counter()
        logger.info("%s 전체 실행 시간: %.4f초", fn.__name__, e - s)
        return r
    return wrap

def extract_stock_code(url: str):
    m = re.search(r'/stocks/[A-Z]?([0-9]{6})/order', url)
    return m.group(1) if m else None

def click_element(driver, locator, timeout=10, retries=2, delay=0.4):
    for _ in range(retries):
        try:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            ).click()
            return True
        except StaleElementReferenceException:
            logger.warning("StaleElementReferenceException, 재시도")
            time.sleep(delay)
    return False

# ──────────────────────────────
# 댓글 1개 파싱
# ──────────────────────────────
def _parse_article(art):
    # 작성자
    author = art.find_element(
        By.CSS_SELECTOR, 'span[style*="font-weight: bold"]'
    ).text.strip()

    # 작성 시각(“6시간 전” 등) — 필요하면 ISO 로 변환
    written_at = art.find_element(
        By.CSS_SELECTOR, 'span[style*="font-weight: normal"]'
    ).text.strip()

    # 더 보기 버튼이 있으면 클릭
    more = art.find_elements(By.XPATH, './/button[.="더 보기"]')
    if more:
        art.parent.execute_script("arguments[0].click()", more[0])

    # 본문
    content_html = art.find_element(
        By.CSS_SELECTOR, 'span[class*="_60z0ev1"]'
    ).get_attribute("innerHTML")
    content = content_html.replace("<br>", "\n").strip()

    # 좋아요 수
    likes_txt = art.find_element(
        By.XPATH, './/div[text()="좋아요 버튼"]/preceding-sibling::span[1]'
    ).text
    likes = int(re.sub(r'\D', '', likes_txt) or 0)

    # 대댓글 수(댓글 펼치기 버튼)
    cmt_txt = art.find_element(
        By.XPATH, './/div[text()="댓글 펼치기 버튼"]/preceding-sibling::span[1]'
    ).text
    comment_cnt = int(re.sub(r'\D', '', cmt_txt) or 0)

    return dict(author=author,
                written_at=written_at,
                content=content,
                likes=likes,
                comment_count=comment_cnt)

# ──────────────────────────────
# 메인 크롤러
# ──────────────────────────────
@time_logger
def fetch_toss_comments(company_name: str, max_scroll=5):
    driver = get_driver()

    # 1) TossInvest 홈 → 검색
    driver.get("https://tossinvest.com/")
    click_element(driver, (By.CLASS_NAME, "u09klc0"))       # 검색창 오픈

    inp = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "_1x1gpvi6"))
    )
    inp.clear()
    inp.send_keys(company_name)
    inp.send_keys(Keys.RETURN)

    # 2) 첫 결과 클릭
    click_element(driver, (By.CLASS_NAME, "u09klc0"))
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]'))
    )

    current_url = driver.current_url
    stock_code  = extract_stock_code(current_url)
    company_name_found = driver.find_element(
        By.XPATH,
        '//*[@id="__next"]/div[1]/div[1]/main/div/div/div/div[3]/div/div[3]/div[1]/span[1]'
    ).text.strip()

    # 3) 커뮤니티 탭
    driver.get(re.sub(r'/order.*', '/community', current_url))

    # 4) 스크롤하여 댓글 로드
    for _ in range(max_scroll):
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
        time.sleep(0.8)

    arts = driver.find_elements(By.XPATH, '//article[contains(@class,"comment")]')
    comments = [_parse_article(art) for art in arts]

    return company_name_found, stock_code, comments
