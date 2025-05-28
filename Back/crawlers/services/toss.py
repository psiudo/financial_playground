import os
import re
import time
import logging
import functools
import datetime # 표준 datetime 임포트
from typing import List, Dict, Tuple, Optional, Union # Optional 또는 Union 추가

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from django.utils import timezone

# 프로젝트의 utils.driver_pool에서 get_driver를 가져옵니다.
# utils 디렉토리가 PYTHONPATH에 있거나, Back 디렉토리에서 실행되는 경우를 가정합니다.
from utils.driver_pool import get_driver

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
# logging.basicConfig(level=LOG_LEVEL,
#                     format='%(asctime)s [%(levelname)s] %(name)s: %(message)s') # Django 프로젝트에서는 settings.py에서 로깅을 설정합니다.
logger = logging.getLogger(__name__)

def time_logger(fn):
    @functools.wraps(fn)
    def wrap(*args, **kwargs):
        s_time = time.perf_counter()
        func_args_str = f"args={args}, kwargs={kwargs}" if args or kwargs else ""
        logger.debug(f"Function '{fn.__name__}' called. {func_args_str}")
        
        r = fn(*args, **kwargs)
        
        e_time = time.perf_counter()
        logger.info(f"Function '{fn.__name__}' execution time: {e_time - s_time:.4f} seconds.")
        return r
    return wrap

def extract_stock_code_from_url(url: str) -> Optional[str]: # Python 3.9 호환을 위해 Union 또는 Optional 사용
    """
    주어진 URL에서 6자리 숫자 또는 알파벳+5자리 숫자로 된 종목 코드를 추출합니다.
    예: /stocks/005930/community, /stocks/A005930/order 등
    """
    if not url:
        return None
    match = re.search(r'/stock(?:s)?/([A-Z]?[0-9]{5,6})(?:/|$|\?)', url)
    if match:
        return match.group(1)
    logger.warning(f"URL에서 종목 코드를 추출하지 못했습니다: {url}")
    return None

def robust_click_element(driver, locator: Tuple[str, str], timeout: int = 15, retries: int = 3, delay_seconds: int = 1) -> bool:
    """
    더 안정적인 요소 클릭 함수 (JavaScript 클릭 포함)
    locator: (By.XPATH, "xpath_string") 형태의 튜플
    """
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", element)
            logger.debug(f"Element clicked via JavaScript: {locator}")
            return True
        except StaleElementReferenceException:
            logger.warning(f"StaleElementReferenceException on attempt {attempt + 1}/{retries} for {locator}")
        except TimeoutException:
            logger.warning(f"TimeoutException (not clickable) on attempt {attempt + 1}/{retries} for {locator}")
        except Exception as e:
            logger.warning(f"Exception clicking element {locator} on attempt {attempt + 1}/{retries}: {e}")
        
        if attempt < retries - 1:
            time.sleep(delay_seconds)
        else: 
            try:
                element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
                element.click() # 마지막 시도는 표준 클릭
                logger.debug(f"Element clicked via standard method: {locator}")
                return True
            except Exception as e_final:
                logger.error(f"Final attempt to click element {locator} failed: {e_final}")
    
    logger.error(f"Robust_click_element 최종 실패: {locator}")
    return False


def parse_toss_relative_time(relative_time_str: str) -> datetime.datetime:
    now = timezone.now()
    if not relative_time_str:
        return now

    cleaned_str = relative_time_str.strip().lower()

    if "방금" in cleaned_str or "just now" in cleaned_str:
        return now

    minutes_match = re.search(r'(\d+)\s*(분|분전|minute|min|m)', cleaned_str)
    if minutes_match:
        return now - datetime.timedelta(minutes=int(minutes_match.group(1)))

    hours_match = re.search(r'(\d+)\s*(시간|시간전|hour|hr|h)', cleaned_str)
    if hours_match:
        return now - datetime.timedelta(hours=int(hours_match.group(1)))

    if "어제" in cleaned_str or "yesterday" in cleaned_str:
        yesterday = now - datetime.timedelta(days=1)
        time_match = re.search(r'(\d{1,2}):(\d{2})', cleaned_str)
        if time_match:
            hour, minute = map(int, time_match.groups())
            return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    date_match_ymd = re.match(r'(\d{4})\s*\.\s*(\d{1,2})\s*\.\s*(\d{1,2})', cleaned_str)
    if date_match_ymd:
        try:
            year, month, day = map(int, date_match_ymd.groups())
            dt_obj = datetime.datetime(year, month, day)
            return timezone.make_aware(dt_obj, timezone.get_current_timezone()) if timezone.is_naive(dt_obj) else dt_obj
        except ValueError:
            logger.warning(f"날짜 형식(YYYY.MM.DD) 파싱 실패: '{cleaned_str}'")
            return now

    date_match_md = re.match(r'(\d{1,2})\s*\.\s*(\d{1,2})\.?', cleaned_str)
    if date_match_md:
        try:
            month, day = map(int, date_match_md.groups())
            dt_obj = datetime.datetime(now.year, month, day)
            aware_dt_obj = timezone.make_aware(dt_obj, timezone.get_current_timezone()) if timezone.is_naive(dt_obj) else dt_obj
            if aware_dt_obj > now :
                 if now.month < month or (now.month == month and now.day < day):
                    dt_obj = datetime.datetime(now.year - 1, month, day)
                    aware_dt_obj = timezone.make_aware(dt_obj, timezone.get_current_timezone()) if timezone.is_naive(dt_obj) else dt_obj
            return aware_dt_obj
        except ValueError:
            logger.warning(f"날짜 형식(MM.DD) 파싱 실패: '{cleaned_str}'")
            return now

    logger.warning(f"알 수 없는 시간 형식: '{cleaned_str}', 현재 시간으로 대체합니다.")
    return now


def _parse_single_toss_comment(article_element, driver_for_js_click) -> Dict[str, Union[str, datetime.datetime, int]]:
    author, written_at_dt, content_text, likes_count = "익명", timezone.now(), "", 0

    author_selectors = [
        'span[class^="tcss-e15d5a"]', 
        'span[style*="font-weight: bold"]',
        'div[data-testid="comment-author"]'
    ]
    for selector in author_selectors:
        try:
            author_el = article_element.find_element(By.CSS_SELECTOR, selector)
            author = author_el.text.strip()
            if author and author != "익명": break # 유효한 작성자명 찾으면 중단
        except NoSuchElementException:
            continue
        except Exception as e_author:
            logger.debug(f"Author parsing error with selector '{selector}': {e_author}")
    if not author : author = "익명"


    time_selectors = [
        'span[class*="time"]',
        'span[style*="color: var(--adaptive_palette-gray-500)"]',
        'span[style*="color:rgb(128, 136, 144)"]', # rgb 값으로도 시도
        'div[data-testid="comment-timestamp"]'
    ]
    written_at_str = ""
    for selector in time_selectors:
        try:
            time_els = article_element.find_elements(By.CSS_SELECTOR, selector)
            for el in time_els: # 여러 요소가 잡힐 수 있으므로 가장 적합한 텍스트 찾기
                el_text = el.text.strip()
                if el_text and (re.search(r'\d', el_text) or any(kw in el_text.lower() for kw in ["분", "시간", "어제", "방금", ".", ":", "just", "ago", "yesterday"])):
                    written_at_str = el_text
                    break
            if written_at_str: break
        except Exception as e_time:
            logger.debug(f"Time parsing error with selector '{selector}': {e_time}")
    
    written_at_dt = parse_toss_relative_time(written_at_str)

    more_button_xpaths = [
        './/button[contains(text(),"더 보기")]',
        './/div[contains(text(),"더 보기") and @role="button"]',
        './/button[contains(normalize-space(), "see more")]'
    ]
    for xpath in more_button_xpaths:
        try:
            more_button = article_element.find_element(By.XPATH, xpath)
            if more_button.is_displayed() and more_button.is_enabled():
                driver_for_js_click.execute_script("arguments[0].click();", more_button)
                time.sleep(0.5) 
                logger.debug(f"'더 보기' 버튼 클릭 성공 (XPath: {xpath})")
                break 
        except NoSuchElementException:
            pass
        except Exception as e_click_more:
            logger.warning(f"'더 보기' 버튼 클릭 중 예외 (XPath: {xpath}): {e_click_more}")

    content_selectors = [
        'div[class*="CommentText__Ellipsis"]', # 새로운 UI 클래스 가능성
        'span[class*="Comment__CommentText-sc-"]', # styled-component 클래스
        'div[class*="comment-content"] span', 
        'div[class*="comment-content"]',    
        'span[class*="_60z0ev1"]',        
        'div[data-testid="comment-body"]'
    ]
    for selector in content_selectors:
        try:
            content_el = article_element.find_element(By.CSS_SELECTOR, selector)
            content_html = content_el.get_attribute("innerHTML")
            content_text = re.sub(r'<br\s*/?>', '\n', content_html).strip()
            content_text = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r' \1 ', content_text)
            content_text = re.sub(r'<[^>]+>', '', content_text).strip()
            if content_text: break
        except NoSuchElementException:
            continue
        except Exception as e_content:
            logger.debug(f"Content parsing error with selector '{selector}': {e_content}")

    like_xpaths = [
        ".//button[contains(@aria-label, '좋아요') or contains(@aria-label, 'like')]//span[string-length(normalize-space(text())) > 0 and number(translate(text(), ',', '')) = number(translate(text(), ',', ''))]",
        './/div[text()="좋아요 버튼"]/preceding-sibling::span[1]', 
        "(.//div[contains(@class, 'Emotion___')]/span)[1]" # 감정 표현 아이콘 옆 숫자 (더 일반적)
    ]
    likes_text_found = "0"
    for xpath in like_xpaths:
        try:
            like_els = article_element.find_elements(By.XPATH, xpath)
            for el in reversed(like_els): # 숫자가 마지막에 오는 경우가 많음
                txt = el.text.strip().replace(',', '') # 쉼표 제거
                if txt.isdigit():
                    likes_text_found = txt
                    break
            if likes_text_found != "0": break 
        except Exception as e_likes:
             logger.debug(f"Likes parsing error with XPath '{xpath}': {e_likes}")
    
    likes_count = int(likes_text_found or 0)

    return dict(author=author, written_at=written_at_dt, content=content_text, likes=likes_count)


@time_logger
def fetch_toss_comments(company_name: str, max_scroll: int = 8, max_comments: int = 150) -> Tuple[Optional[str], Optional[str], List[Dict[str, any]]]:
    driver = None
    crawled_comments: List[Dict[str, any]] = []
    actual_company_name_on_page = company_name
    actual_stock_code_on_page = None

    try:
        driver = get_driver()
        if not driver:
            logger.critical("WebDriver instance could not be created. Crawler cannot proceed.")
            return actual_company_name_on_page, actual_stock_code_on_page, []

        logger.info(f"Toss investing community comment crawling started for: '{company_name}'")
        driver.get("https://tossinvest.com/")
        
        search_button_locators = [
            (By.CSS_SELECTOR, "button[aria-label='검색'], button[aria-label='Search']"),
            (By.XPATH, "//button[.//img[contains(@class, 'search-icon')] or .//span[text()='검색']]") # 아이콘 클래스 또는 텍스트
        ]
        if not any(robust_click_element(driver, loc, timeout=10) for loc in search_button_locators):
            logger.error("Failed to find or click the search icon on Toss Securities.")
            return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments

        search_input_locator = (By.CSS_SELECTOR, "input[placeholder*='종목 또는 별명'], input[placeholder*='stock or ticker']")
        try:
            search_input_el = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(search_input_locator))
            search_input_el.clear()
            search_input_el.send_keys(company_name)
            time.sleep(1.2) # Wait for autocomplete/search results
            search_input_el.send_keys(Keys.ENTER)
            logger.info(f"Search term '{company_name}' submitted.")
        except Exception as e_input:
            logger.error(f"Error during search input for '{company_name}': {e_input}")
            return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments
        
        try:
            WebDriverWait(driver, 25).until(lambda d: "/stock/" in d.current_url or "/stocks/" in d.current_url)
            current_url = driver.current_url
            logger.info(f"Navigated to stock related page: {current_url}")
            
            actual_stock_code_on_page = extract_stock_code_from_url(current_url)
            
            name_locators = ["h1[class*='name']", "div[class*='NameContainer'] > strong", "span[class*='stock__name']"]
            for selector in name_locators:
                try:
                    name_element = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector))) # 짧은 대기
                    actual_company_name_on_page = name_element.text.strip()
                    if actual_company_name_on_page and actual_company_name_on_page != company_name:
                        logger.info(f"Actual company name found on page: '{actual_company_name_on_page}' (Searched for: '{company_name}')")
                    break
                except: continue
            
            if not actual_stock_code_on_page:
                logger.warning(f"Could not extract stock code from URL '{current_url}' after searching for '{company_name}'. Attempting to click first search result.")
                first_result_xpath = "(//a[contains(@href, '/stock/') and .//strong[contains(text(),'"+company_name[:3]+"')] ])[1]" # 더 정확한 첫번째 결과 xpath
                try:
                    if robust_click_element(driver, (By.XPATH, first_result_xpath), timeout=10):
                        WebDriverWait(driver, 15).until(lambda d: extract_stock_code_from_url(d.current_url) is not None)
                        current_url = driver.current_url
                        actual_stock_code_on_page = extract_stock_code_from_url(current_url)
                        logger.info(f"Clicked first search result. New URL: {current_url}, Stock Code: {actual_stock_code_on_page}")
                    else:
                        raise Exception("Failed to click first search result or extract code after click.")
                except Exception as e_first_click:
                    logger.error(f"Failed to navigate to stock detail page for '{company_name}': {e_first_click}")
                    return actual_company_name_on_page, None, crawled_comments
            
            if not actual_stock_code_on_page:
                logger.error(f"Unable to determine stock code for '{company_name}' after search and potential first result click.")
                return actual_company_name_on_page, None, crawled_comments

        except TimeoutException:
            logger.error(f"Timeout while navigating to stock detail page for '{company_name}'. Current URL: {driver.current_url}")
            return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments

        community_url = f"https://tossinvest.com/stock/{actual_stock_code_on_page}/community"
        logger.info(f"Navigating to community page: {community_url}")
        driver.get(community_url)

        try:
            WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "virtual-scroll-container")] | //article[contains(@class,"comment")] | //div[contains(text(),"아직 작성된 게시글이 없어요")] | //div[contains(text(),"No posts yet")]'))
            )
            logger.info(f"Community page loaded for {actual_stock_code_on_page}.")
        except TimeoutException:
            logger.error(f"Timeout loading community page content for {actual_stock_code_on_page}. URL: {driver.current_url}")
            return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments

        no_posts_xpaths = ['//div[contains(text(),"아직 작성된 게시글이 없어요")]', '//div[contains(text(),"No posts yet")]']
        if any(driver.find_elements(By.XPATH, xpath) for xpath in no_posts_xpaths):
            logger.info(f"No community posts found for '{actual_company_name_on_page}' ({actual_stock_code_on_page}).")
            return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        parsed_comment_unique_ids = set() # 댓글 고유 ID (작성자+시간+내용 앞부분) 저장

        for i in range(max_scroll):
            if len(crawled_comments) >= max_comments:
                logger.info(f"Reached max comments limit ({max_comments}). Stopping scroll.")
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.8) # Increased wait time for content loading

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and i > 1: # 스크롤 변화가 없으면 (두 번 이상 시도 후)
                logger.info("No change in scroll height, assuming all comments loaded.")
                break
            last_height = new_height
            
            article_elements = driver.find_elements(By.XPATH, '//article[contains(@class,"comment-item--") or contains(@class, "CommentItem__CommentArticle")]') # 더욱 구체적인 클래스 타겟팅
            if not article_elements: # 대체 선택자
                 article_elements = driver.find_elements(By.XPATH, '//article[contains(@class,"comment")]')


            logger.debug(f"Scroll {i+1}/{max_scroll}: Found {len(article_elements)} article elements. Total collected: {len(crawled_comments)}")
            
            newly_added_this_scroll = 0
            for art_el in article_elements:
                if len(crawled_comments) >= max_comments: break
                try:
                    comment_data = _parse_single_toss_comment(art_el, driver)
                    # 더 나은 중복 체크: 작성자, 시간(분단위), 내용 첫 20자로 해시 또는 튜플 만들어 사용
                    comment_id_str = f"{comment_data['author']}_{comment_data['written_at'].strftime('%Y%m%d%H%M')}_{comment_data['content'][:30]}"
                    if comment_data.get("content") and comment_id_str not in parsed_comment_unique_ids:
                        comment_data['stock_code'] = actual_stock_code_on_page
                        comment_data['source'] = 'TossSecuritiesCommunity'
                        crawled_comments.append(comment_data)
                        parsed_comment_unique_ids.add(comment_id_str)
                        newly_added_this_scroll +=1
                except Exception as e_parse_loop:
                    logger.warning(f"Error parsing individual comment: {e_parse_loop}", exc_info=False)
            
            if newly_added_this_scroll == 0 and i > 2: # 3번 연속 새 댓글 없으면 중단
                logger.info("No new comments added in the last few scrolls. Stopping.")
                break
        
        logger.info(f"Crawling and parsing finished. Total {len(crawled_comments)} comments collected for: {actual_company_name_on_page} ({actual_stock_code_on_page})")
        return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments

    except WebDriverException as e_wd:
        logger.error(f"WebDriverException during crawling for '{company_name}': {e_wd}", exc_info=True)
        return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments
    except NotImplementedError as nie:
        logger.critical(f"WebDriver load failure (NotImplementedError): {nie}. Check 'utils.driver_pool.get_driver()'.")
        return actual_company_name_on_page, actual_stock_code_on_page, []
    except Exception as e_main:
        logger.error(f"Unexpected major error in fetch_toss_comments for '{company_name}': {e_main}", exc_info=True)
        return actual_company_name_on_page, actual_stock_code_on_page, crawled_comments
    finally:
        if driver:
            # utils.driver_pool.py의 atexit 핸들러가 종료를 담당하므로, 여기서는 quit() 호출 안 함
            logger.info(f"Finished using WebDriver for '{company_name}'. Driver instance managed by driver_pool.")
            pass