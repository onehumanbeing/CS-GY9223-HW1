#!/bin/bash
mkdir -p package
cd package
python3.10 -m pip install --target . opensearch-py>=2.0.0 requests_aws4auth
cp ../lambdafunctions/cc_hw1_lf2.py lambda_function.py
zip -r ../lambda_function.zip .
cd ..
rm -rf package
aws lambda update-function-code \
    --function-name arn:aws:lambda:us-east-1:654654400451:function:cc_hw1_lf2 \
    --zip-file fileb://lambda_function.zip
rm lambda_function.zip
echo "Done"

# Push to lambda function