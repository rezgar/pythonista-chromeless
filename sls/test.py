from selenium import webdriver
from tempfile import TemporaryDirectory
from webdriver_manager.chrome import ChromeDriverManager
from server import ChromelessServer

with TemporaryDirectory() as dirname:
    server = ChromelessServer()
    driver = server.gen_chrome(None, dirname)
    driver.get('https://google.com')
    print(driver.title)