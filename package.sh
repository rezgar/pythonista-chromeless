#!/bin/bash

mkdir -p lambda-package
mkdir -p lambda-package/versions
cp sls/server.py lambda-package/
cp sls/picklelib.py lambda-package/
cp sls/fonts.conf lambda-package/
cp -r sls/versions/*.py lambda-package/versions/
cp sls/requirements.txt lambda-package/


pip install -r sls/requirements.txt --target ./lambda-package
zip -r lambda.zip ./lambda-package
rm -r ./lambda-package