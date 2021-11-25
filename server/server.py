import os
import shutil
import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

from picklelib import loads, dumps  # imports in Dockerfile
import helper

import json
import marshal
import textwrap
from versions import ChromelessServerVerNone
from versions import ChromelessServerVer1
import traceback
from tempfile import TemporaryDirectory
import os
import re
import time

os.environ['FONTCONFIG_PATH'] = '/opt/fonts'

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

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
    print(arg)
    required_version = arg['REQUIRED_SERVER_VERSION'] if isinstance(arg, dict) else None
    
    ChormelessServerClass = {
        2: ChromelessServer,  # latest
        1: ChromelessServerVer1,
        None: ChromelessServerVerNone,
    }[required_version]

    if required_version is None:
        arg = dumps(arg)  # dump again

    return ChormelessServerClass().recieve(arg)


class ChromelessServer():
    SERVER_VERSION = 2

    def gen_chrome(self, options, dirname):
        if options is None:
            options = get_default_chrome_options(dirname)
        
        chromedriver=ChromeDriverManager(path="/tmp/chromedriver").install()

        return webdriver.Chrome(chromedriver, options=options)

    def gen_firefox(self, options, dirname):
        if options is None:
            options = get_default_firefox_options(dirname)
        
        geckodriver = GeckoDriverManager(path="/tmp/geckodriver").install()
        profile = webdriver.FirefoxProfile(profile_directory=dirname)

        return webdriver.Firefox(
            firefox_profile = profile,
            firefox_binary = '/usr/bin/firefox',
            executable_path = geckodriver,
            options=options,
            service_log_path='/tmp/geckodriver.log')

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

    def recieve(self, arguments):
        with TemporaryDirectory() as dirname:  # e.x. /tmp/tmpwc6a08sz
            return self._recieve(arguments, dirname)

    def _recieve(self, arguments, dirname):
        browser = None
        try:
            invoked_func_name = arguments["invoked_func_name"]
            codes = arguments["codes"]
            arg = arguments["arg"]
            kw = arguments["kw"]
            options = arguments["options"]
            browser = self.gen_chrome(options, dirname)

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

def get_default_firefox_options(dirname):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("-headless")
    firefox_options.add_argument("-safe-mode")
    firefox_options.add_argument('-width 2560')
    firefox_options.add_argument('-height 1440')

    return firefox_options
def get_default_chrome_options(dirname):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    #options.add_argument("--test-type=integration")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument("--single-process")
    #options.add_argument("window-size=2560x1440") # https://github.com/aws-samples/serverless-ui-testing-using-selenium/blob/5454ea9ddc13a0f1ad397d9c22f1e4db58fc39fc/app.py#L66
    options.add_argument("--window-size=1600,1024") # https://github.com/GoogleChrome/chrome-launcher/blob/master/docs/chrome-flags-for-tools.md#window--screen-management
    
    options.add_argument("--enable-automation")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(f"--user-data-dir={dirname}/user-data")
    options.add_argument("--homedir=" + dirname)
    options.add_argument(f"--data-path={dirname}/data-path")
    options.add_argument(f"--disk-cache-dir={dirname}/cache-dir")
    options.add_argument(f"--disk-cache-size=104857600")
    options.add_argument(f"--profile-directory={dirname}/profile")
    options.add_argument(f"--quarantine-dir={dirname}/quarantine")

    # Stealth
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--incognito")

    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    return options
