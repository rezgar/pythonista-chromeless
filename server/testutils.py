from selenium import webdriver
from tempfile import TemporaryDirectory
from webdriver_manager.chrome import ChromeDriverManager
from server import ChromelessServer, get_default_chrome_options
from helper import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium_stealth import stealth

import inspect, marshal

import pickle
import zlib
import base64

import re
import time

def execute_server(func):
    server = ChromelessServer()
    return server.recieve({
        "invoked_func_name": "test",
        "codes": {
            "test": (inspect.getsource(func), marshal.dumps(func.__code__))
        },
        "arg": [],
        "kw": {},
        "options": None,
        "REQUIRED_SERVER_VERSION": 2,
    })

def execute_custom(func):
    with TemporaryDirectory() as dirname:
        server = ChromelessServer()
        options = get_default_chrome_options(dirname) 
        #options = webdriver.ChromeOptions()
            
        browser = server.gen_chrome(options, dirname)

        stealth(browser,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        return func(browser)
