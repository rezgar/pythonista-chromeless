from selenium import webdriver
from tempfile import TemporaryDirectory
from webdriver_manager.chrome import ChromeDriverManager
from server import ChromelessServer, get_default_chrome_options

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

with TemporaryDirectory() as dirname:
    server = ChromelessServer()
    options = get_default_chrome_options(dirname) #webdriver.ChromeOptions()
    browser = server.gen_chrome(options, dirname)

    stealth(browser,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    email = "rezgar.cadro@devfactory.com"
    password = "4I7WJ4sSPaqiHBKQ#5vH"
    
    selectors = {
        'login': 'lucid-button.sso-button.google',
        'email': 'input[type=email]',
        'email_next': '#identifierNext button',
        'password': 'input[type=password]',
        'password_next': '#passwordNext button'
    }

    browser.get('https://lucid.app/users/login#/')

    google_login_button = browser.find_element_by_css_selector(selectors['login'])
    google_login_button.click()

    WebDriverWait(browser, 10).until(lambda driver: "google.com" in driver.current_url)

    browser.find_element_by_css_selector(selectors['email']).send_keys(email)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['email_next'])))
    browser.find_element_by_css_selector(selectors['email_next']).click()

    # create action chain object
    action = ActionChains(browser)    
    action.move_to_element(browser.find_element_by_css_selector('h1')).click().perform()

    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['password'])))

    browser.find_element_by_css_selector(selectors['password']).send_keys(password)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['password_next'])))
    browser.find_element_by_css_selector(selectors['password_next']).click()

    WebDriverWait(browser, 30).until(lambda driver: "lucid" in driver.current_url)

    print(browser.title)