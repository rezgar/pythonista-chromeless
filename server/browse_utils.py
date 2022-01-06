import sys
import os

import boto3
from selenium import webdriver
from tempfile import TemporaryDirectory
from webdriver_manager.chrome import ChromeDriverManager
from server import ChromelessServer, get_default_chrome_options
import helper

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium_stealth import stealth

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'client')))
from client import Chromeless

import inspect, marshal
import picklelib
import types

def browse(entry_function_name, functions, boto3_session = None, remote = False, **kwargs):
    # Remote server
    if remote:
        browser = Chromeless(
            function_name = 'chromeless-server-prod',
            boto3_session = boto3_session)

        for function in functions:
            browser.attach(function)

        return getattr(browser, entry_function_name)()
    # Local server
    else:
        server = ChromelessServer(**kwargs)
        
        return picklelib.loads(server.recieve({
            "invoked_func_name": entry_function_name,
            "codes": { function.__name__: (inspect.getsource(function), marshal.dumps(function.__code__)) for function in functions},
            "arg": sys.argv,
            "kw": {},
            "options": None
        }))