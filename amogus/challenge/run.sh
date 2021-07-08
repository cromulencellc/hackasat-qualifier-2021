#!/bin/bash

export KEY1="e9b9d3f2d275ca5759e60c8ee18425dc"
export KEY2="f58ebfe38a88eb2d760e64acb062585f"
export KEY3="05f1e0f77ce8fbb75532e8023056e4e6"

LD_LIBRARY_PATH=${GLIBC_227_64}/ ./challenge &

python3 ./voter_async.py -i 0 & 
python3 ./voter_async.py -i 1 &

python3 ./player_voter.py

