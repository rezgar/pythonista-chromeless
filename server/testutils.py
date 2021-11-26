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

sys.path.append(os.path.abspath('./client'))
from client import Chromeless

import inspect, marshal
import picklelib
import types

def browse(entry_function_name, functions, remote = False, **kwargs):
    # Remote server
    if remote:
        sts_client = boto3.client('sts')
        credentials=sts_client.assume_role(
            RoleArn = "arn:aws:iam::162174280605:role/chromeless-server-orgaccess-role-prod",
            RoleSessionName = f"Rezgar-Test",
        )['Credentials']

        boto3_session = boto3.Session(
            aws_access_key_id = credentials['AccessKeyId'],
            aws_secret_access_key = credentials['SecretAccessKey'],
            aws_session_token = credentials['SessionToken']
        )

        return Chromeless(
            function_name = 'chromeless-server-prod',
            boto3_session = boto3_session)
    
    # Local server
    else:
        server = ChromelessServer(**kwargs)
        
        return picklelib.loads(server.recieve({
            "invoked_func_name": entry_function_name,
            "codes": { name: (inspect.getsource(functions[name]), marshal.dumps(functions[name].__code__)) for name in functions},
            "arg": [],
            "kw": {},
            "options": None,
            "REQUIRED_SERVER_VERSION": 2,
        }))