from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import re
import time

def change_proxy(browser, proxy):
   capabilities = browser.desired_capabilities['chrome'].copy()
   capabilities['proxy'] = {
    'http': proxy,
    'https': proxy,
    'no_proxy': 'localhost,127.0.0.1'
   } if proxy else None
   # https://chromedriver.chromium.org/capabilities
   # https://developers.perfectomobile.com/display/TT/How+to+pass+Chrome+options+as+capabilities
   # If not set, tries to open UI browser in headless mode (doesn't respect properties)
   capabilities['goog:chromeOptions'] = {
     "args": [ arg for arg in browser.__dict__['options'].capabilities['goog:chromeOptions']['args'] if \
        # If inherited, browsing continues in the original window without switching to new session
        '/tmp/' not in arg and not arg.startswith('--remote-debugging-port')
      ]
   }

   cookies = browser.get_cookies()
   url = browser.current_url
  
   session = browser.start_session(capabilities)
   browser.switch_to.default_content()
   browser.get(url)

   for cookie in cookies:
     browser.add_cookie(cookie)
  
   browser.get(url)

def login_with_google(browser, email, password):
    selectors = {
        'email': 'input[type=email]',
        'email_next': '#identifierNext button',
        'password': 'input[type=password]',
        'password_next': '#passwordNext button'
    }

    # https://gist.github.com/ikegami-yukino/51b247080976cb41fe93#gistcomment-3455633
    # This link comes from the oauth playground, which is an official tool Google provides to test oauth applications.
    browser.get('https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow')

    WebDriverWait(browser, 60).until(lambda driver: "google.com" in driver.current_url)

    WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['email'])))
    browser.find_element_by_css_selector(selectors['email']).send_keys(email)
    WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['email_next'])))
    browser.find_element_by_css_selector(selectors['email_next']).click()

    # create action chain object
    action = ActionChains(browser)
    action.move_to_element(browser.find_element_by_css_selector('h1')).click().perform()

    WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['password'])))

    browser.find_element_by_css_selector(selectors['password']).send_keys(password)
    WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['password_next'])))
    browser.find_element_by_css_selector(selectors['password_next']).click()

    WebDriverWait(browser, 60).until(lambda driver: driver.current_url.startswith("https://developers.google.com"))

    return browser

def login_with_slack(browser, workspace, email, password):
    selectors = {
        'login': 'lucid-button.sso-button.slack',
        'workspace': 'input#domain',
        'workspace_next': 'button[type=submit]',
        'email': 'input#email',
        'password': 'input#password',
        'signin': '#signin_btn',
        'permissions_accept_form': '#oauth_authorize_confirm_form',
        'accept_permissions': 'button[type=submit]',
        'accept_cookies': '#onetrust-accept-btn-handler'
    }

    browser.get('https://lucid.app/users/login#/')

    google_login_button = browser.find_element_by_css_selector(selectors['login'])
    google_login_button.click()

    WebDriverWait(browser, 60).until(lambda driver: "slack.com" in driver.current_url)

    WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['workspace'])))
    browser.find_element_by_css_selector(selectors['workspace']).send_keys(workspace)
    browser.find_element_by_css_selector(selectors['workspace_next']).click()

    WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['email'])))
    browser.find_element_by_css_selector(selectors['email']).send_keys(email)
    browser.find_element_by_css_selector(selectors['password']).send_keys(password)

    browser.find_element_by_css_selector(selectors['signin']).click()
    
    WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['permissions_accept_form'])))
    
    WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['accept_permissions'])))
    browser.find_element_by_css_selector(selectors['accept_cookies']).click()
    WebDriverWait(browser, 60).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, selectors['accept_cookies'])))
    browser.find_element_by_css_selector(selectors['accept_permissions']).click()

    WebDriverWait(browser, 60).until(lambda driver: "slack.com" not in driver.current_url)

    return browser

def wheel_element(browser, element, deltaY = 120, offsetX = 0, offsetY = 0):
  error = element._parent.execute_script("""
    var element = arguments[0];
    var deltaY = arguments[1];
    var box = element.getBoundingClientRect();
    var clientX = box.left + (arguments[2] || box.width / 2);
    var clientY = box.top + (arguments[3] || box.height / 2);
    var target = element.ownerDocument.elementFromPoint(clientX, clientY);

    for (var e = target; e; e = e.parentElement) {
      if (e === element) {
        target.dispatchEvent(new MouseEvent('mouseover', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new MouseEvent('mousemove', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new WheelEvent('wheel',     {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY, deltaY: deltaY}));
        return;
      }
    }    
    return "Element is not interactable";
    """, element, deltaY, offsetX, offsetY)
  if error:
    raise WebDriverException(error)