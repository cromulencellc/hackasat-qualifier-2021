
#!/bin/bash
echo "Starting ground station"
cd /home/ground/fprime
VIRTUAL_ENV=/home/ground/fprime/fprime-venv
export PATH="$VIRTUAL_ENV/bin:$PATH"
fprime-gds -n --dictionary dict/RefTopologyAppDictionary.xml --gui-addr 0.0.0.0 --tts-port 5001 > /tmp/ground.log 2>&1 &
# fprime-gds -n --dictionary dict/RefTopologyAppDictionary.xml --gui-addr 0.0.0.0