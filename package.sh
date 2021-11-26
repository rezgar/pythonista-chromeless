#!/bin/bash

rm client/lambda.zip
mkdir -p lambda-package
cp server/server.py lambda-package/
cp server/helper.py lambda-package/
cp server/picklelib.py lambda-package/
cp server/fonts.conf lambda-package/
cp server/requirements.txt lambda-package/

pip install -r server/requirements.txt --target ./lambda-package
cd lambda-package && zip -r ../client/lambda.zip * && cd ..
rm -r ./lambda-package