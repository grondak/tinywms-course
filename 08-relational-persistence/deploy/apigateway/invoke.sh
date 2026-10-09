#!/bin/sh
set -eu
printf '%s\n' '{"httpMethod":"GET","path":"/inventory","resource":"/inventory","headers":{"accept":"application/json"},"queryStringParameters":null,"body":null,"isBase64Encoded":false}' | python3 src/lambda_inventory.py
