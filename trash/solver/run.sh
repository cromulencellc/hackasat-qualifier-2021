#!/bin/bash
# starts the conjunction-junction solver
docker build -t conjunction-junction-solver .
docker run -it conjunction-junction-solver
