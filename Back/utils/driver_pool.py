# back/utils/driver_pool.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import atexit, threading, logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

_lock   = threading.Lock()
_driver = None

def get_driver():
    global _driver
    with _lock:
        if _driver is None:
            logger.info("🚀 ChromeDriver 새로 실행")
            opts = Options()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--blink-settings=imagesEnabled=false")
            _driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=opts
            )
        else:
            logger.info("♻️ 기존 ChromeDriver 재사용 중")
    return _driver

@atexit.register
def _quit_driver():
    if _driver:
        logger.info("🛑 ChromeDriver 종료")
        _driver.quit()
