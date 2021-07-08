#!/bin/bash

BASE_IP=${SERVICE_HOST:-localhost}
BASE_PORT=${SERVICE_PORT:-5000}

su -l --shell=/bin/bash --whitelist=FLAG -c "/run_space.sh ${FLAG}" space
# ./run_ground.sh 
su -l --shell=/bin/bash -c '/run_ground.sh' ground

WEB_IP=${BASE_IP}
WEB_PORT=${BASE_PORT}
GDS_IP=${BASE_IP}
GDS_PORT=$((BASE_PORT + 1))

echo "Challenge Web Page Starting at http://${WEB_IP}:${WEB_PORT}"
echo "CLI available at ${GDS_IP}:${GDS_PORT}"
# export FLAG=""
# timeRemaining=900
timeRemaining=${TIMEOUT:-900}
# flag="NONE"
while [ ${timeRemaining} -gt 0 ]; do
    # echo "Time Remaining ${timeRemaining}"
    # echo "${flag}"
    if [ $((timeRemaining % 60)) -eq 0 ]; then
        echo "Time remaining to solve: ${timeRemaining} seconds"
    fi
    # if [ ${timeRemaining} -lt 0 ];then
        
    #     exit 0;
    # fi
    # flag=$(su -l -c 'echo $SAT_FLAG' space)
    timeRemaining=$((timeRemaining - 1))
    sleep 1
done
echo "Time is up. Try again with new ticket...."
exit 0
# tail -f /tmp/ground.log
