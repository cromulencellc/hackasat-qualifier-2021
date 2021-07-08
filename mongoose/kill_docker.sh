#!/bin/bash

docker kill `docker ps | grep mongoose_mayhem:challenge | cut -f1 -d' '`
