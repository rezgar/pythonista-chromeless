## Introduction

This is a Selenium Python server hosted on AWS Lambda. Clients can call it directly or via AWS API Gateway, and have the server execute their Selenium Python scripts and return the result.

This is a fork of the [pythonista-chromeless](https://github.com/umihico/pythonista-chromeless.git) project by **umihico**.

**Added functionality:**
- Evergreen Chrome
- Stealth (powered by `selenium-stealth`)
- Proxy/Tor support (including password-protected proxies)
- Debugging tools (running scripts in different modes (stealth, headless etc) against a local or a remote Selenium server)

Enabling Stealth and using Proxies allows bypassing most of the anti-automation checks, including Google's.

## Deploying the Selenium server Lambda

`PROXY=https://username:password@host:port sls deploy --region YOUR_REGION`

This will deploy a Lambda and an API Gateway in front of it.

## Running Selenium scripts using the Selenium server

The idea behind this project is for the client to send the script to the server, which then executes it in its own context. The `client` utility abstracts away this communication and allows the client to invoke functions in a semi-usual manner.

**Usage:**
```
chrome = Chromeless()
chrome.attach(your_selenium_script_function)
chrome.attach(selenium_scripts_called_by_your_selenium_script_function)

result = chrome.your_selenium_script_function(param1, param2)
```

Selenium server Lambda can be called directly or via API Gateway (added limitations: max 30 sec execution duration). 

**Caveat**: Only "attached" functions are sent to the server, not their dependencies
This means you **can not reference** functions/variables/imports declared outside of the function body, unless they are also "attached"

## Debugging Selenium scripts

You can use `server/debug_utils.py` to conveniently execute and debug your Selenium Python scripts in different modes:
+ Locally or against a remote server (Lambda)
+ In a regular or headless mode
+ In a regular or stealth mode
+ Via an unauthenticated or authenticated proxy
+ Via Tor

**Sample test script:**
```
  sts_client = boto3.client('sts')
  credentials=sts_client.assume_role(
      RoleArn = "arn:aws:iam::99999999999:role/chromeless-server-orgaccess-role-prod",
      RoleSessionName = f"Selenium-Debugger",
  )['Credentials']

  boto3_session = boto3.Session(
      aws_access_key_id = credentials['AccessKeyId'],
      aws_secret_access_key = credentials['SecretAccessKey'],
      aws_session_token = credentials['SessionToken'],
      region_name = "us-east-1"
  )
  
  print(browse(
    selenium_test_script.__name__,
    functions = [ selenium_test_script, expand_folder_path, navigate_to_folder, create_folder ],
    boto3_session = boto3_session,
    remote = True,
    headless = True,
    use_tor = False,
    stealth = True,
    proxy = "https://name:password@45.150.7.78:99990",
  ))
```

### [License](https://github.com/umihico/pythonista-chromeless/blob/master/LICENSE)
The project is licensed by **umihico** under the MIT license.
