import boto3
import re
import sys, os
import inspect
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'server')))
from browse_utils import *

remote = False
headless = False
use_tor = False
stealth = True
proxy = "https://Selrezgarcadro:C9e8DcC@45.150.7.78:45785"

def selenium_test_script(browser, *arg):
  folder_path = "Shared with Me/Internal Specs"
  folder_name = "Victor"
  
  # browser.get('http://icanhazip.com')
  # return browser.page_source

  browser.lucidchart_login_with_google("spec.automation@devfactory.com", "aquifer-L-DpTmnihB=F2")
  #browser.change_proxy(None) # Remove proxy after login

  document_id = browser.create_document()
  return document_id

def lucidchart_login_with_google(browser, email, password):
    selectors = {
        'login': 'lucid-button.sso-button.google',
        'email': 'input[type=email]',
        'email_next': '#identifierNext button',
        'password': 'input[type=password]',
        'password_next': '#passwordNext button'
    }

    browser.get('https://lucid.app/users/login#/')

    WebDriverWait(browser, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['login'])))
    google_login_button = browser.find_element_by_css_selector(selectors['login'])
    google_login_button.click()

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

    WebDriverWait(browser, 300).until(lambda driver: "https://lucid.app/documents" in driver.current_url)
    browser.change_proxy(None) # Remove proxy after login

    return browser.title

def create_document(browser):
    # Create a Blank Diagram
    browser.get('https://lucid.app/lucidchart/editNew?loaddialog=InviteModal&beaconFlowId=5074D1DD29930701')
    # https://lucid.app/lucidchart/2c1bc7df-d85d-47a2-8dd9-b88aabd1de64/edit?loaddialog=InviteModal&beaconFlowId=DCF10D7520BE72A9

    WebDriverWait(browser, 60).until(lambda driver: driver.current_url.startswith("https://lucid.app/lucidchart/"))

    document_id = re.search("https:\/\/lucid\.app\/lucidchart\/([\w-]+)", browser.current_url).group(1)
    return document_id

def rename_document(browser, document_id, title):
    browser.get(f'https://lucid.app/lucidchart/{document_id}/edit')
    
    selectors = {
        'title_start_edit': 'lucid-input#document_title',
        'title_input': 'lucid-input#document_title input',
        'viewport': 'lucid-viewport',
        'saved_indicator': '.save-status',
    }

    # element_to_be_clickable?
    WebDriverWait(browser, 300).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selectors['title_start_edit'])))

    # Edit document title
    action = ActionChains(browser)
    action.move_to_element(browser.find_element_by_css_selector(selectors['title_start_edit'])).click().perform()
    WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['title_start_edit'] + ".focused")))

    browser.find_element_by_css_selector(selectors['title_input']).clear()
    browser.find_element_by_css_selector(selectors['title_input']).send_keys(title)
    
    # Blur to accept editing
    action = ActionChains(browser)
    action.move_to_element(browser.find_element_by_css_selector(selectors['viewport'])).click().perform()

    # Wait while save completes
    WebDriverWait(browser, 300).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, selectors['saved_indicator']), "Saving..."))
    WebDriverWait(browser, 300).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, selectors['saved_indicator']), "Saved"))

def expand_folder_path(browser, folder_path):
    selectors = {
        "documents_arrow": "lucid-platform-tab#documents > lucid-finger .toggle-arrow",
        "documents_arrow_expanded": "lucid-platform-tab#documents > lucid-finger .toggle-arrow .icon.expanded"
    }
    # Expand Documents (special case)
    action = ActionChains(browser)
    action.move_to_element(browser.find_element_by_css_selector(selectors['documents_arrow'])).click().perform()
    WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['documents_arrow_expanded'])))

    # Expand folders under Documents
    folder_names = folder_path.split('/')
    i = 0
    for folder_name in folder_names: 
        i += 1
        expand_arrow_xpath = f"//lucid-folder-node/lucid-collapse-bar/*[contains(@class, 'header-wrapper') and contains(.,'{folder_name}')]//span[contains(@class, 'toggle-arrow')]"
        expand_arrow_node = browser.find_element_by_xpath(expand_arrow_xpath)
        folder_node = expand_arrow_node.find_element_by_xpath('ancestor::lucid-folder-node[1]') # point to the actual "lucid-folder-node" (no built-in support to do it more intelligently)
        folder_id = re.search("folder-node-(\w+)", folder_node.get_attribute("data-selenium-id")).group(1)

        # Scroll to the node
        scrollable_area = browser.find_element_by_css_selector('lucid-platform-tabs lucid-scrollable')
        browser.wheel_element(scrollable_area, folder_node.get_property('offsetTop'))
        WebDriverWait(browser, 300).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"lucid-folder-node[data-selenium-id='folder-node-{folder_id}']")))

        # We need to expand up to the final folder's parent to be able to interact with it, but still return the last folder
        if i < len(folder_names):
            # Expand folder
            action = ActionChains(browser)
            action.move_to_element(expand_arrow_node).click().perform()

            # Wait while the node is being expanded
            WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"lucid-folder-node[data-selenium-id='folder-node-{folder_id}'] > lucid-collapse-bar > .content lucid-folder-node")))

    return folder_node

def navigate_to_folder(browser, folder_path):
    browser.expand_folder_path(folder_path)

    folder_name = folder_path.split('/')[-1]
    folder_header_xpath = f"//lucid-folder-node/lucid-collapse-bar/*[contains(@class, 'header-wrapper') and contains(.,'{folder_name}')]"
    folder_header_node = browser.find_element_by_xpath(folder_header_xpath)
    folder_title_node = folder_header_node.find_element_by_css_selector('.edit-text-container')
    folder_node = folder_header_node.find_element_by_xpath('ancestor::lucid-folder-node[1]')
    folder_id = re.search("folder-node-(\w+)", folder_node.get_attribute("data-selenium-id")).group(1)

    # Click doesn't properly go through if we use folder_node or folder_header. Although from the UI it's clear that you can click at any part of the container, with automation the results results are reliable only when clicking on the title
    action = ActionChains(browser)
    action.move_to_element(folder_title_node).click().perform()

    # Wait until the data is loaded on the screen. Sadly, there's no one good indicator, so we have to do a sequence
    WebDriverWait(browser, 300).until(EC.url_contains(folder_id))
    # Times out, it's not always that WebDriver can catch this temporary event happening
    # WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"lucid-file-entry-list .animate-in")))
    WebDriverWait(browser, 300).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, f"lucid-file-entry-list .animate-in")))

    return folder_node

def create_folder(browser, folder_name):
    selectors = {
        "content_area": '.scrolling-list',
        "new_folder_menu_item": "#menu-item-newfolder",
        "new_folder_name_input": "lucid-prompt-dialog lucid-input input",
        "new_folder_submit": "lucid-dialog-footer lucid-deprecated-button.highlight"
    }

    #action chain object
    action = ActionChains(browser)
    action.move_to_element(browser.find_element_by_css_selector(selectors['content_area'])).context_click().perform()

    WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['new_folder_menu_item'])))
    browser.find_element_by_css_selector(selectors['new_folder_menu_item']).click()

    WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['new_folder_name_input'])))
    folder_name_input = browser.find_element_by_css_selector(selectors['new_folder_name_input'])
    folder_name_input.clear()
    folder_name_input.send_keys(folder_name)

    browser.find_element_by_css_selector(selectors['new_folder_submit']).click()

def move_document(browser, document_id, folder_path):
    folder_node = browser.expand_folder_path(folder_path)

    selectors = {
        "document_item": f'lucid-folder-entry[data-selenium-id="doc-{document_id}"] .wrapper'
    }

    document_item = browser.find_element_by_css_selector(selectors['document_item'])

    action = ActionChains(browser)
    action.drag_and_drop(document_item, folder_node).perform()

    # Wait until the element is gone from the page (meaning move completed)
    WebDriverWait(browser, 300).until(EC.staleness_of(document_item))

## Utility ##

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

def main():
  #boto3.setup_default_session(region_name = "us-east-1")

  #sts_client = boto3.client('sts')
  #credentials=sts_client.assume_role(
  #    RoleArn = "arn:aws:iam::138088458349:role/chromeless-server-orgaccess-role-prod",
  #    RoleSessionName = f"Rezgar-Test",
  #)['Credentials']

  #boto3_session = boto3.Session(
  #    aws_access_key_id = credentials['AccessKeyId'],
  #    aws_secret_access_key = credentials['SecretAccessKey'],
  #    aws_session_token = credentials['SessionToken'],
  #    region_name = "us-east-1"
  #)
  
  print(browse(
    selenium_test_script.__name__,
    functions =  [obj for name,obj in inspect.getmembers(sys.modules[__name__]) if (inspect.isfunction(obj) and obj.__module__ == __name__)],
      # [ selenium_test_script, expand_folder_path, navigate_to_folder, create_folder ],
    #boto3_session = boto3_session,
    remote = remote,
    headless = headless,
    use_tor = use_tor,
    proxy = proxy,
    stealth = stealth
  ))

if __name__ == '__main__':
  main()