from selenium import webdriver
from tempfile import TemporaryDirectory
from webdriver_manager.chrome import ChromeDriverManager

def get_default_options(dirname):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("headless")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--hide-scrollbars")
    options.add_argument("enable-automation")
    #options.add_argument("--enable-logging")
    #options.add_argument("--log-level=0") # Invalid log-level value
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--homedir=" + dirname)
    options.add_argument(f"--user-data-dir={dirname}/user-data")
    options.add_argument(f"--data-path={dirname}/data-path")
    options.add_argument(f"--disk-cache-dir={dirname}/cache-dir")
    return options


with TemporaryDirectory() as dirname:
    options = get_default_options(dirname)
    chromedriver=ChromeDriverManager(path="/tmp/chromedriver").install()
    driver = webdriver.Chrome(chromedriver, options = options)