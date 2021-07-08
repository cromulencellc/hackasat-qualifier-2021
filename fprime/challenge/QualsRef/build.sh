#!/bin/bash

echo "Build QualsRef Deployment"
flag=$1

echo "Cleanup to good state prior to build"
fprime-util purge -f

if [ -z "${FLAG_PASSCODE}" ]; then
    passcode=$(python3 codegen.py)
    # passcode="123456_654321_qwerty"
    echo "Set FlagPasscode to ${passcode}"
    export FLAG_PASSCODE=${passcode}
    echo "FLAG_PASSCODE=${passcode}" >> env.ini
fi

echo "Generate fprime build cache"
fprime-util generate

echo "Run Build"
fprime-util build

# echo "Write FlagData to file .FlagData"
# flagData=${FLAG:-flag{test123test123987654321}}
# export FLAG=${flagData}
# echo "${flag}" > $(pwd)/FlagData.txt

if [ $? -eq 0 ]; then
    echo "Complete. Passcode: ${FLAG_PASSCODE}, FLAG: ${FLAG}"
else
    echo "Build Failed"
fi