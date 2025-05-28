# Back/crawlers/services/toss.py
import os, re, time, logging, functools, datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from django.utils import timezone # Django의 timezone 사용
# from utils.driver_pool import get_driver # 이 부분은 실제 driver_pool.py 내용에 따라 주석 해제 또는 수정 필요

# get_driver() 함수 임시 정의 (실제 utils.driver_pool.py 내용으로 대체 필요)
# 이 함수가 WebDriver 인스턴스를 반환해야 합니다.
# 예시: from selenium import webdriver
def get_driver():
    # 실제 WebDriver 설정 및 반환 로직 필요
    # logger.debug("임시 get_driver 호출됨")
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # 예시: 헤드리스 모드
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome(options=options)
    # return driver
    raise NotImplementedError("utils.driver_pool.get_driver() 함수를 실제 WebDriver 로직으로 구현해야 합니다.")


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# time_logger 함수 정의를 fetch_toss_comments 함수 정의 앞으로 이동
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
    if not m: # /order가 없는 community URL도 고려
        m = re.search(r'/stocks/[A-Z]?([0-9]{6})/community', url)
    return m.group(1) if m else None

def click_element(driver, locator, timeout=10, retries=3, delay=0.5):
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            return True
        except StaleElementReferenceException:
            logger.warning(f"StaleElementReferenceException, 재시도 ({attempt + 1}/{retries})")
            time.sleep(delay)
        except Exception as e:
            logger.warning(f"Click_element 예외 발생 ({locator}): {e}, 재시도 ({attempt + 1}/{retries})")
            time.sleep(delay)
    logger.error(f"Click_element 최종 실패: {locator}")
    return False

# 헬퍼 함수: 상대 시간을 datetime 객체로 변환
def parse_relative_time(relative_time_str):
    now = timezone.now()
    if not relative_time_str: # 빈 문자열이나 None이면 현재 시간 반환
        return now
        
    if "방금" in relative_time_str or "Just now" in relative_time_str.lower():
        return now
    
    minutes_match = re.search(r'(\d+)\s*(분|minute|min) 전', relative_time_str)
    if minutes_match:
        minutes_ago = int(minutes_match.group(1))
        return now - datetime.timedelta(minutes=minutes_ago)
    
    hours_match = re.search(r'(\d+)\s*(시간|hour|hr) 전', relative_time_str)
    if hours_match:
        hours_ago = int(hours_match.group(1))
        return now - datetime.timedelta(hours=hours_ago)
    
    if "어제" in relative_time_str or "Yesterday" in relative_time_str.lower():
        yesterday = now - datetime.timedelta(days=1)
        time_match = re.search(r'(\d{1,2}):(\d{2})', relative_time_str)
        if time_match:
            hour, minute = map(int, time_match.groups())
            return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    date_match_md = re.match(r'(\d{1,2})\.(\d{1,2})\.', relative_time_str) # MM.DD. 형식
    if date_match_md:
        try:
            month, day = map(int, date_match_md.groups())
            # 올해의 해당 날짜로 설정
            parsed_date = datetime.datetime(now.year, month, day, tzinfo=now.tzinfo)
            if parsed_date > now and (now.month < month or (now.month == month and now.day < day)): # 미래 날짜로 보이면 작년으로
                 parsed_date = datetime.datetime(now.year -1, month, day, tzinfo=now.tzinfo)
            return parsed_date
        except ValueError:
            logger.warning(f"날짜 형식 파싱 실패 (MM.DD.): {relative_time_str}")
            return now 
            
    date_match_ymd = re.match(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', relative_time_str) # YYYY.MM.DD 형식
    if date_match_ymd:
        try:
            year, month, day = map(int, date_match_ymd.groups())
            return datetime.datetime(year, month, day, tzinfo=now.tzinfo)
        except ValueError:
            logger.warning(f"날짜 형식 파싱 실패 (YYYY.MM.DD): {relative_time_str}")
            return now

    logger.warning(f"알 수 없는 시간 형식: '{relative_time_str}', 현재 시간으로 대체합니다.")
    return now


# ──────────────────────────────
# 댓글 1개 파싱
# ──────────────────────────────
def _parse_article(art): # driver 인스턴스를 인자로 받을 필요가 없음 (art에서 모두 해결)
    author = "익명"
    written_at_dt = timezone.now() # 기본값
    content = ""
    likes = 0

    try:
        author_element = art.find_element(By.CSS_SELECTOR, 'span[style*="font-weight: bold"]')
        author = author_element.text.strip() if author_element else "익명"
    except Exception:
        logger.debug("작성자 정보 파싱 중 오류 발생 (기본값 사용)")

    try:
        written_at_element = art.find_element(By.CSS_SELECTOR, 'span[style*="font-weight: normal"]')
        written_at_str = written_at_element.text.strip() if written_at_element else ""
        written_at_dt = parse_relative_time(written_at_str)
    except Exception:
        logger.debug("작성 시간 정보 파싱 중 오류 발생 (기본값 사용)")

    try:
        more_buttons = art.find_elements(By.XPATH, './/button[contains(text(),"더 보기")]')
        if more_buttons:
            try:
                # JavaScript 클릭이 더 안정적일 수 있습니다.
                # art.parent는 WebElement이므로 execute_script를 직접 호출할 수 없습니다.
                # driver 객체가 필요합니다. 이 함수 스코프에 없다면, click_element 사용하거나 driver 전달해야 합니다.
                # 여기서는 단순 click() 시도. StaleElementReferenceException 대비 필요.
                more_buttons[0].click() 
                time.sleep(0.3) # DOM 변경 대기
            except Exception as e_click:
                logger.warning(f"더 보기 버튼 클릭 중 오류: {e_click}")
    except Exception:
        logger.debug("더 보기 버튼 처리 중 오류 발생")
        
    try:
        content_element = art.find_element(By.CSS_SELECTOR, 'span[class*="_60z0ev1"]') 
        content_html = content_element.get_attribute("innerHTML") if content_element else ""
        content = content_html.replace("<br>", "\n").strip()
    except Exception:
        logger.debug("본문 내용 파싱 중 오류 발생 (기본값 사용)")

    try:
        likes_element = art.find_element(By.XPATH, './/div[text()="좋아요 버튼"]/preceding-sibling::span[1]')
        likes_txt = likes_element.text if likes_element else "0"
        likes = int(re.sub(r'\D', '', likes_txt) or 0)
    except Exception:
        logger.debug("좋아요 수 파싱 중 오류 발생 (기본값 사용)")
        
    # comment_count는 현재 모델에 없으므로 제거
    # try:
    #     cmt_element = art.find_element(By.XPATH, './/div[text()="댓글 펼치기 버튼"]/preceding-sibling::span[1]')
    #     cmt_txt = cmt_element.text if cmt_element else "0"
    #     comment_cnt = int(re.sub(r'\D', '', cmt_txt) or 0)
    # except Exception:
    #     logger.debug("댓글 수 파싱 중 오류 발생 (기본값 사용)")
    #     comment_cnt = 0
        
    return dict(author=author, # tasks.py에서 Comment 모델의 author 필드에 사용
                written_at=written_at_dt,
                content=content,
                likes=likes, # tasks.py에서 Comment 모델의 likes 필드에 사용
                # comment_count=comment_cnt # 필요시 모델에 추가하고 사용
                )

# ──────────────────────────────
# 메인 크롤러 함수
# ──────────────────────────────
@time_logger # 데코레이터는 이제 이 함수 위에 정의된 time_logger를 참조합니다.
def fetch_toss_comments(company_name: str, max_scroll=5):
    driver = None
    try:
        driver = get_driver() # WebDriver 인스턴스 가져오기
        if driver is None: # get_driver가 None을 반환할 경우 처리
            logger.error("WebDriver를 가져오지 못했습니다.")
            return company_name, None, []

        logger.info(f"Toss 투자 커뮤니티 댓글 크롤링 시작: {company_name}")
        driver.get("https://tossinvest.com/")
        
        # 검색 아이콘 클릭 (더 명확한 selector로 변경)
        search_button_locators = [
            (By.CSS_SELECTOR, "button[aria-label='검색']"), 
            (By.CLASS_NAME, "u09klc0") # 이전 selector 유지 (폴백)
        ]
        search_button_clicked = False
        for locator in search_button_locators:
            if click_element(driver, locator, timeout=5, retries=1):
                search_button_clicked = True
                break
        if not search_button_clicked:
            logger.error("토스 증권 검색 아이콘 클릭 실패")
            return company_name, None, []

        # 검색 입력창 (더 명확한 selector로 변경)
        search_input_locator = (By.CSS_SELECTOR, "input[placeholder='종목 또는 별명을 검색해보세요']")
        try:
            inp = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(search_input_locator)
            )
            inp.clear()
            inp.send_keys(company_name)
            time.sleep(0.7) # 검색어 입력 후 자동완성 또는 결과 로딩 대기
            inp.send_keys(Keys.RETURN)
        except Exception as e:
            logger.error(f"검색어 입력 실패 ({company_name}): {e}")
            return company_name, None, []
            
        # 종목 상세 페이지로 이동했는지 확인 (커뮤니티 탭 존재 여부로 판단)
        try:
            WebDriverWait(driver, 20).until( # 시간 증가
                EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/community") and (contains(text(),"커뮤니티") or .//span[contains(text(),"커뮤니티")])] | //button[contains(text(),"커뮤니티")]'))
            )
            logger.info(f"종목 상세 페이지 로드 확인: {company_name}")
        except Exception as e:
            logger.error(f"종목 상세 페이지 로드 실패 또는 커뮤니티 탭 찾기 실패 ({company_name}): {driver.current_url} - {e}")
            # 현재 URL이 검색 결과 페이지인지 확인하여 첫번째 결과 클릭 시도 (선택적)
            return company_name, None, []

        current_url = driver.current_url
        stock_code_found = extract_stock_code(current_url)
        
        company_name_found_on_page = company_name # 기본값
        try:
            # 회사명 확인 (더 안정적인 방법 필요)
            # 예시: header 태그 내의 h1 또는 특정 data-testid 속성 사용
            # name_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "header h1"))) 
            # company_name_found_on_page = name_element.text.strip()
            # logger.info(f"크롤러에서 확인된 회사명: {company_name_found_on_page}")
            pass # 이 부분은 실제 페이지 구조에 맞춰 정확한 selector를 찾아야 합니다.
        except Exception:
            logger.warning(f"크롤러에서 정확한 회사명 확인 실패. 입력된 '{company_name}' 사용.")


        if not stock_code_found:
            logger.error(f"URL에서 종목 코드를 추출하지 못했습니다: {current_url} (회사명: {company_name})")
            return company_name_found_on_page, None, []

        # 커뮤니티 탭 URL로 직접 이동
        community_url = f"https://tossinvest.com/stock/{stock_code_found}/community"
        logger.info(f"커뮤니티 URL로 이동: {community_url}")
        driver.get(community_url)
        
        try:
            WebDriverWait(driver, 15).until(
                 EC.presence_of_element_located((By.XPATH, '//article[contains(@class,"comment")] | //div[contains(text(),"아직 작성된 게시글이 없어요")] | //div[contains(text(),"로그인하고")]'))
            )
        except Exception as e:
            logger.error(f"커뮤니티 페이지 로드 실패 ({stock_code_found}): {e}")
            return company_name_found_on_page, stock_code_found, []
            
        # "아직 작성된 게시글이 없어요" 또는 "로그인하고" 메시지 확인
        if driver.find_elements(By.XPATH, '//div[contains(text(),"아직 작성된 게시글이 없어요")] | //div[contains(text(),"로그인하고")]'):
            logger.info(f"'{company_name_found_on_page}' 종목의 토스 커뮤니티에 게시글이 없거나 로그인이 필요합니다.")
            return company_name_found_on_page, stock_code_found, []

        # 스크롤하여 댓글 로드
        for i in range(max_scroll):
            logger.info(f"Scrolling down ({i+1}/{max_scroll}) for {stock_code_found}")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5) # 댓글 로딩 대기 시간 증가

        # 댓글 article 요소 찾기
        article_elements = driver.find_elements(By.XPATH, '//article[contains(@class,"comment")]')
        
        comments = []
        if not article_elements:
             logger.info(f"스크롤 후에도 댓글 요소를 찾지 못했습니다: {company_name_found_on_page} ({stock_code_found}).")
        
        logger.info(f"{len(article_elements)}개의 댓글 article 요소를 찾았습니다. 파싱 시작...")
        for art_idx, art_element in enumerate(article_elements):
            try:
                comment_dict = _parse_article(art_element) # WebElement 전달
                comment_dict['stock_code'] = stock_code_found # 일관성을 위해 추가
                comment_dict['source'] = 'TossSecuritiesCommunity' # 출처 명시
                comments.append(comment_dict)
            except Exception as e_parse:
                logger.error(f"댓글 파싱 중 오류 (인덱스 {art_idx}): {e_parse}", exc_info=False) # exc_info=True로 하면 전체 스택 트레이스 로깅
                continue
        
        logger.info(f"총 {len(comments)}개의 댓글 파싱 완료: {company_name_found_on_page} ({stock_code_found})")
        return company_name_found_on_page, stock_code_found, comments

    except Exception as e_main:
        logger.error(f"fetch_toss_comments 함수 실행 중 주요 오류 발생 ({company_name}): {e_main}", exc_info=True)
        return company_name, None, []
    finally:
        if driver:
            # driver_pool을 사용한다면 반환 로직 (예: driver_pool.release_driver(driver))
            # 단일 드라이버 사용 시에는 quit()
            try:
                driver.quit() 
                logger.info("WebDriver 종료됨.")
            except Exception as e_quit:
                logger.error(f"WebDriver 종료 중 오류: {e_quit}")