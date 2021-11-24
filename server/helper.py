from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import re
import time 

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

    WebDriverWait(browser, 300).until(lambda driver: "google.com" in driver.current_url)

    WebDriverWait(browser, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['email'])))
    browser.find_element_by_css_selector(selectors['email']).send_keys(email)
    WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['email_next'])))
    browser.find_element_by_css_selector(selectors['email_next']).click()

    # create action chain object
    action = ActionChains(browser)
    action.move_to_element(browser.find_element_by_css_selector('h1')).click().perform()

    WebDriverWait(browser, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['password'])))

    browser.find_element_by_css_selector(selectors['password']).send_keys(password)
    WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['password_next'])))
    browser.find_element_by_css_selector(selectors['password_next']).click()

    WebDriverWait(browser, 300).until(lambda driver: driver.current_url.startswith("https://developers.google.com"))

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
        'accept_permissions': 'button[type=submit]'
    }

    browser.get('https://lucid.app/users/login#/')

    google_login_button = browser.find_element_by_css_selector(selectors['login'])
    google_login_button.click()

    WebDriverWait(browser, 300).until(lambda driver: "slack.com" in driver.current_url)

    WebDriverWait(browser, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['workspace'])))
    browser.find_element_by_css_selector(selectors['workspace']).send_keys(workspace)
    browser.find_element_by_css_selector(selectors['workspace_next']).click()

    WebDriverWait(browser, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['email'])))
    browser.find_element_by_css_selector(selectors['email']).send_keys(email)
    browser.find_element_by_css_selector(selectors['password']).send_keys(password)

    browser.find_element_by_css_selector(selectors['signin']).click()
    
    WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['permissions_accept_form'])))
    browser.find_element_by_css_selector(selectors['accept_permissions']).click()

    WebDriverWait(browser, 300).until(lambda driver: "slack.com" not in driver.current_url)

    return browser