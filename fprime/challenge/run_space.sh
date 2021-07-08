echo "Starting spacecraft"
FLAG=$1
cd /home/space/fprime/
export SAT_FLAG=${FLAG}
./satellite.exe -a 127.0.0.1 -p 50000 > /tmp/satellite.log 2>&1 &
sleep 5
export SAT_FLAG="ThisIsNotTheFlagYouAreLookingFor"