import argparse, sys
import sys, os
#sys.path.append(os.path.abspath('./server'))
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'server')))
from browse_utils import *
import inspect
import re

def main():
  parser=argparse.ArgumentParser()
  parser.add_argument('--document', help='Source Google Document ID', required=True)
  parser.add_argument('--snapshot', help='Snapshot name', required=True)
  parser.add_argument('--email', help='Google account email', required=True)
  parser.add_argument('--password', help='Google account password', required=True)
  parser.add_argument('--proxy', help='HTTPS proxy, format: [https://username:password@host:port]')
  parser.add_argument('--headless', help='Headless mode', action='store_true')

  if len(sys.argv) == 1:
    print(parser.format_help())
    return

  args, unknown = parser.parse_known_args()

  print(selenium_main.__code__.co_filename)

  print(browse(
    selenium_main.__name__,
    functions =  [obj for name,obj in inspect.getmembers(sys.modules[__name__]) if (inspect.isfunction(obj) and obj.__module__ == __name__)],
    remote = False,
    headless = args.headless,
    use_tor = False,
    stealth = True,
    proxy = args.proxy
  ))

def selenium_main(browser, *arg):
  parser = argparse.ArgumentParser()

  parser.add_argument('--document', help='Source Google Document ID', required=True)
  parser.add_argument('--snapshot', help='Snapshot name', required=True)
  parser.add_argument('--email', help='Google account email', required=True)
  parser.add_argument('--password', help='Google account password', required=True)

  args, unknown = parser.parse_known_args(arg)

  document_id = browser.copy_document(
    args.email,
    args.password,
    args.document,
    args.snapshot,
    True,
    True
  )

  return f'https://docs.google.com/document/d/{document_id}/edit'
  
def copy_document(browser, email, password, document_id, new_name, copy_comments, include_resolved_comments = False):
    if email and password:
        browser.login_with_google(email, password)

    browser.get(f'https://docs.google.com/document/d/{document_id}/edit')

    selectors = {
        "file_menu": f'#docs-file-menu[aria-disabled=false]',
        "copy_submenu": f'.goog-menuitem-label[aria-label$=" c"]',
        "dialog_filename": ".docs-copydocdialog-filenameinput",
        "dialog_copy_share": ".docs-copydocdialog-collaboratorcheckbox", # Not available for the "SpecAutomation account for some reason"
        "dialog_copy_comments": ".docs-copydocdialog-commentcheckbox",
        "dialog_include_resolved_comments": ".docs-copydocdialog-includeresolvedcommentscheckbox",
        "dialog_ok": "button[name=ok]"
    }

    WebDriverWait(browser, 300).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selectors['file_menu'])))
    file_menu = browser.find_element_by_css_selector(selectors['file_menu'])
    file_menu.click()

    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selectors['copy_submenu'])))
    copy_submenu = browser.find_element_by_css_selector(selectors['copy_submenu'])
    copy_submenu.click()

    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selectors['dialog_filename'])))

    # Copy dialog input
    browser.find_element_by_css_selector(selectors['dialog_filename']).send_keys(new_name)

    if copy_comments:
        browser.find_element_by_css_selector(selectors['dialog_copy_comments']).click()
    if include_resolved_comments:
        browser.find_element_by_css_selector(selectors['dialog_include_resolved_comments']).click()

    original_tab = browser.window_handles[0]
    original_tab_count = len(browser.window_handles)
    browser.find_element_by_css_selector(selectors['dialog_ok']).click()
    
    # Switch to new tab
    WebDriverWait(browser, 300).until(EC.number_of_windows_to_be(original_tab_count + 1))
    newWindow = [window for window in browser.window_handles if window != original_tab][0]
    browser.switch_to.window(newWindow)

    document_id = re.search('https://docs.google.com/document/d/([\w\-]+)', browser.current_url).group(1)
    return document_id

if __name__ == '__main__':
  main()