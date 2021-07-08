#!/bin/sh 
echo "Starting up Service on tcp:${SERVICE_HOST}:${SERVICE_PORT}"
mkdir -p /challenge/bank
echo "Your King is in another castle" > /challenge/flag1.txt
echo ${FLAG} > /challenge/bank/flag2.txt

env -i /challenge/runner  &

while read line
do
	echo "Nothing here"
done < "${1:-/dev/stdin}"
