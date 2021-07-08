#!/bin/bash

docker run -it --rm --net="host" fprime-exploitation:solver
# docker run -it --rm --net="host" --entrypoint=/bin/bash fprime-exploitation:solver