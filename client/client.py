import inspect
import marshal
import boto3
import boto3.session
import botocore
import json
import sys
import requests
import os

import pickle
import zlib
import base64

def dumps(obj):
    return base64.b64encode(zlib.compress(pickle.dumps(obj))).decode()

def loads(obj):
    return pickle.loads(zlib.decompress(base64.b64decode(obj.encode())))

class Chromeless():
    def __init__(self, gateway_url=None, gateway_apikey=None, chrome_options=None, function_name='chromeless-server-prod', logger = None, boto3_session = None):
        self.gateway_url = gateway_url
        self.gateway_apikey = gateway_apikey
        self.options = chrome_options
        if function_name == 'chromeless-server-prod' and 'CHROMELESS_SERVER_FUNCTION_NAME' in os.environ:
            function_name = os.environ['CHROMELESS_SERVER_FUNCTION_NAME']
        self.function_name = function_name
        self.logger = logger
        self.boto3_session = boto3_session if boto3_session else boto3.session.Session()
        self.codes = {}

    def attach(self, method):
        self.codes[method.__name__] = inspect.getsource(
            method), marshal.dumps(method.__code__)

    def __getattr__(self, name):
        if name in self.codes:
            self.invoked_func_name = name
            return self.__invoke
        raise AttributeError(
            f"{self.__class__.__name__} object has no attribute {name}")

    def __invoke(self, *arg, **kw):
        dumped = dumps({
            "invoked_func_name": self.invoked_func_name,
            "codes": self.codes,
            "arg": arg,
            "kw": kw,
            "options": self.options
        })
        if self.function_name == "local":
            method = self.__invoke_local
        elif self.gateway_url is not None:
            method = self.__invoke_api
        else:
            method = self.__invoke_lambda
        response, metadata = loads(method(dumped))
        if metadata['status'] == "error":
            raise Exception(response)
        else:
            return response

    def __invoke_api(self, dumped):
        headers = {'x-api-key': self.gateway_apikey}
        return requests.post(self.gateway_url, headers=headers,
                             json={'dumped': dumped}).json()['result']

    def __invoke_local(self, dumped):
        response = requests.post(
            "http://chromeless:8080/2015-03-31/functions/function/invocations", json={'dumped': dumped})
        return response.text

    def __invoke_lambda(self, dumped):
        config = botocore.config.Config(retries={'max_attempts': 3}, read_timeout=900, connect_timeout=600)
        client = self.boto3_session.client('lambda', config=config)

        response = client.invoke(
            FunctionName=self.function_name,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=json.dumps({'dumped': dumped})
        )
        response_body = response['Payload'].read().decode()
        
        if self.logger:
            self.logger.info(json.dumps(response_body))

        return response_body
