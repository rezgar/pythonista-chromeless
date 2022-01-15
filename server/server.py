import argparse
import sys, os
import shutil
import types
import zipfile
from copy import copy, deepcopy
#from selenium import webdriver
from seleniumwire import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium_stealth import stealth

from picklelib import loads, dumps  # imports in Dockerfile
import helper

import json
import marshal
import textwrap
import traceback
from tempfile import TemporaryDirectory
import os
import re
import time

os.environ['FONTCONFIG_PATH'] = '/opt/fonts'

from webdriver_manager.chrome import ChromeDriverManager

def remove_tmpfiles():
    for filename in os.listdir('/tmp'):
        file_path = os.path.join('/tmp', filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def handler(event=None, context=None):
    remove_tmpfiles()
    if 'dumped' in event:
        dumped = event['dumped']
        return invoke(dumped)
    else:
        dumped = json.loads(event['body'])['dumped']
        return {
            'statusCode': 200,
            'body': json.dumps({'result': invoke(dumped)}),
            "headers": {
                'Content-Type': "application/json",
                'Access-Control-Allow-Origin': '*',
            }
        }

def invoke(dumped):
    arg = loads(dumped)
    return ChromelessServer(proxy = os.getenv("PROXY")).receive(arg)

class ChromelessServer():
    def __init__(self, headless = True, use_tor = False, proxy = None, stealth = True):
      self.headless = headless
      self.use_tor = use_tor
      self.proxy = proxy
      self.stealth = stealth
      self.default_options, self.default_seleniumwire_options = get_default_chrome_options(self)

    def open_browser(self, dirname, options = None, seleniumwire_options = None):
        options, seleniumwire_options = generate_session_options(self, dirname, options, seleniumwire_options)
        
        chromedriver=ChromeDriverManager(path="/tmp/chromedriver").install()

        browser = webdriver.Chrome(chromedriver, options=options, seleniumwire_options = seleniumwire_options)

        #browser.
        # TODO: Fix the issue with param overrides not storing values. Find some other collection in Browser
        browser.__dict__['options'] = options
        browser.__dict__['seleniumwire_options'] = seleniumwire_options

        return browser

    def parse_code(self, code, name):
        inspected, marshaled = code
        try:
            try:
                exec(inspected)
            except Exception:
                exec(textwrap.dedent(inspected))
            func = locals()[name]
        except Exception:
            func = types.FunctionType(
                marshal.loads(marshaled), globals(), name)
        return func

    def receive(self, arguments):
        with TemporaryDirectory() as dirname:  # e.x. /tmp/tmpwc6a08sz
            return self._receive(arguments, dirname)

    def _receive(self, arguments, dirname):
        browser = None
        try:
            invoked_func_name = arguments["invoked_func_name"]
            codes = arguments["codes"]
            arg = arguments["arg"]
            kw = arguments["kw"]
            options_override = arguments.get("options")
            seleniumwire_options_override = arguments.get("seleniumwire_options")
            browser = self.open_browser(dirname, options_override, seleniumwire_options_override)

            if self.stealth:
                stealth(browser,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                )

            # Attach helpers
            for name, code in [(name, code) for name, code in helper.__dict__.items() if callable(code)]:
                setattr(browser, name, types.MethodType(code, browser))

            # Attach code "attach"ed by the user
            for name, code in codes.items():
                func = self.parse_code(code, name)
                setattr(browser, name, types.MethodType(func, browser))

            metadata = {'status': 'success'}
            response = getattr(browser, invoked_func_name)(*arg, **kw)
        except Exception:
            metadata = {'status': 'error'}
            response = "\n".join([
                "\n============== CHROMELESS TRACEBACK IN LAMBDA START ==============",
                traceback.format_exc(),
                "============== CHROMELESS TRACEBACK IN LAMBDA END ================\n",
            ])
        finally:
            if browser:
                browser.quit()

        return dumps((response, metadata))

def get_default_chrome_options(self):
    options = webdriver.ChromeOptions()

    options.set_capability('pageLoadStrategy', 'none')

    seleniumwire_options = {}
    
    if self.use_tor:
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
    
    if self.proxy:
        seleniumwire_options['proxy'] = {
            'http': self.proxy,
            'https': self.proxy,
            'no_proxy': 'localhost,127.0.0.1'
        }

    if self.headless:
        options.add_argument("--headless")
        options.add_argument("--no-zygote")
        options.add_argument("--single-process")

    options.add_argument("--no-sandbox")
    #options.add_argument("--test-type=integration")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-tools")

    #options.add_argument("window-size=2560x1440") # https://github.com/aws-samples/serverless-ui-testing-using-selenium/blob/5454ea9ddc13a0f1ad397d9c22f1e4db58fc39fc/app.py#L66
    options.add_argument("--window-size=1600,1024") # https://github.com/GoogleChrome/chrome-launcher/blob/master/docs/chrome-flags-for-tools.md#window--screen-management
    
    options.add_argument("--enable-automation")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--profile-directory=Default")
    
    if self.stealth:
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--incognito")

    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')

    return options, seleniumwire_options

def generate_session_options(self, dirname, options_override, seleniumwire_options_override):
  options = deepcopy(self.default_options)
  seleniumwire_options = deepcopy(self.default_seleniumwire_options)

  options.add_argument(f"--user-data-dir={dirname}/user-data")
  options.add_argument("--homedir=" + dirname)
  options.add_argument(f"--data-path={dirname}/data-path")
  options.add_argument(f"--disk-cache-dir={dirname}/cache-dir")
  options.add_argument(f"--disk-cache-size=104857600")
  options.add_argument(f"--profile-directory={dirname}/profile")
  options.add_argument(f"--quarantine-dir={dirname}/quarantine")

  if options_override:
    for key in options_override:
      setattr(options, key, options_override[key])

  if seleniumwire_options_override:
    for key in seleniumwire_options_override:
      setattr(seleniumwire_options, key, seleniumwire_options_override[key])

  return options, seleniumwire_options