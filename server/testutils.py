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

import inspect, marshal
import picklelib
import types

def browse_headless(entry_function_name, functions):
    server = ChromelessServer()
    
    return picklelib.loads(server.recieve({
        "invoked_func_name": entry_function_name,
        "codes": { name: (inspect.getsource(functions[name]), marshal.dumps(functions[name].__code__)) for name in functions},
        "arg": [],
        "kw": {},
        "options": None,
        "REQUIRED_SERVER_VERSION": 2,
    }))

def browse_graphical(entry_function_name, functions):
    with TemporaryDirectory() as dirname:
        server = ChromelessServer()
        options = webdriver.ChromeOptions()
        #options = get_default_chrome_options(dirname) 
            
        browser = server.gen_chrome(options, dirname)

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

        for name in functions:
            setattr(browser, name, types.MethodType(functions[name], browser))

        return functions[entry_function_name](browser)
