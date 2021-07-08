#!/bin/bash

docker kill `docker ps | grep mars:challenge | cut -f1 -d' '`
